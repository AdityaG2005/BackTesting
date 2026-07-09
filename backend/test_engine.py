from app.db.session import SessionLocal
from app.models import Instrument, Bar
from app.core.strategies.moving_average_crossover import MovingAverageCrossover
from app.core.engine import BacktestEngine


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

        strategy = MovingAverageCrossover()
        engine = BacktestEngine(strategy, starting_cash=10000)

        result = engine.run(bars, ticker="AAPL")

        print(f"Starting cash: ${result['starting_cash']:.2f}")
        print(f"Final value:   ${result['final_value']:.2f}")
        total_return = ((result['final_value'] - result['starting_cash']) / result['starting_cash']) * 100
        print(f"Total return:  {total_return:.2f}%")
        print(f"Total trades:  {len(result['trades'])}")

        print("\n--- Trade Log ---")
        for trade in result['trades']:
            status = "OPEN" if trade.is_open else "CLOSED"
            pnl_str = f"${trade.pnl:.2f}" if trade.pnl is not None else "N/A"
            print(f"{trade.entry_timestamp.date()} -> "
                  f"{trade.exit_timestamp.date() if trade.exit_timestamp else '...'} | "
                  f"{status} | qty={trade.quantity} | "
                  f"entry=${trade.entry_price:.2f} | "
                  f"exit={'$' + format(trade.exit_price, '.2f') if trade.exit_price else 'N/A'} | "
                  f"pnl={pnl_str}")

    finally:
        session.close()


if __name__ == "__main__":
    main()

    