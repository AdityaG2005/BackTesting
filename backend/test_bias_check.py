from app.db.session import SessionLocal
from app.models import Instrument, Bar
from app.core.strategies.moving_average_crossover import MovingAverageCrossover
from app.core.strategies.rsi_mean_reversion import RSIMeanReversion
from app.core.bias_check import check_lookahead_bias


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

        print("--- Lookahead-Bias Check: MovingAverageCrossover ---")
        result = check_lookahead_bias(
            strategy_factory=lambda: MovingAverageCrossover(),
            bars=bars,
            ticker="AAPL"
        )
        print(f"Passed: {result['passed']}")
        print(f"Checked points: {result['checked_points']}")
        if result['mismatches']:
            for m in result['mismatches']:
                print(f"  MISMATCH at {m['timestamp']}: full={m['full_signal']} vs truncated={m['truncated_signal']}")

        print("\n--- Lookahead-Bias Check: RSIMeanReversion ---")
        result = check_lookahead_bias(
            strategy_factory=lambda: RSIMeanReversion(),
            bars=bars,
            ticker="AAPL"
        )
        print(f"Passed: {result['passed']}")
        print(f"Checked points: {result['checked_points']}")
        if result['mismatches']:
            for m in result['mismatches']:
                print(f"  MISMATCH at {m['timestamp']}: full={m['full_signal']} vs truncated={m['truncated_signal']}")

    finally:
        session.close()


if __name__ == "__main__":
    main()

    