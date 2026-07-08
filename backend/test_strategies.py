from app.db.session import SessionLocal
from app.models import Instrument, Bar
from app.core.strategies.moving_average_crossover import MovingAverageCrossover
from app.core.strategies.rsi_mean_reversion import RSIMeanReversion
from app.core.strategy import SignalType


def run_strategy(strategy, bars, ticker):
    print(f"\n--- {strategy.__class__.__name__} on {ticker} ---")
    history = []
    signal_count = 0

    for bar in bars:
        bar.ticker = ticker  # attach ticker for use inside on_bar
        signal = strategy.on_bar(bar, history)
        history.append(bar)

        if signal.signal_type != SignalType.HOLD:
            signal_count += 1
            print(f"{signal.timestamp.date()} | {signal.signal_type.value.upper()} | {signal.reason}")

    print(f"Total non-HOLD signals: {signal_count}")


def main():
    session = SessionLocal()
    try:
        instrument = session.query(Instrument).filter_by(ticker="AAPL").first()
        bars = (
            session.query(Bar)
            .filter_by(instrument_id=instrument.id)
            .order_by(Bar.timestamp)
            .all()
        )

        run_strategy(MovingAverageCrossover(), bars, "AAPL")
        run_strategy(RSIMeanReversion(), bars, "AAPL")

    finally:
        session.close()


if __name__ == "__main__":
    main()

    