from app.db.session import SessionLocal
from app.models import Instrument, Bar
from app.core.strategies.moving_average_crossover import MovingAverageCrossover
from app.core.engine import BacktestEngine
from app.core.metrics import (
    calculate_sharpe,
    calculate_sortino,
    calculate_cagr,
    calculate_max_drawdown,
    calculate_win_rate,
)
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

        strategy = MovingAverageCrossover()
        engine = BacktestEngine(strategy, starting_cash=10000)
        result = engine.run(bars, ticker="AAPL")

        equity_curve = result["equity_curve"]
        trades = result["trades"]
        starting_value = result["starting_cash"]
        final_value = result["final_value"]

        sharpe = calculate_sharpe(equity_curve)
        sortino = calculate_sortino(equity_curve)
        cagr = calculate_cagr(starting_value, final_value, len(equity_curve))
        max_dd = calculate_max_drawdown(equity_curve)
        win_rate = calculate_win_rate(trades)

        bias_result = check_lookahead_bias(
            strategy_factory=lambda: MovingAverageCrossover(),
            bars=bars,
            ticker="AAPL"
        )

        print("=" * 50)
        print("BACKTEST REPORT: MovingAverageCrossover on AAPL")
        print("=" * 50)
        print(f"Starting cash:   ${starting_value:,.2f}")
        print(f"Final value:     ${final_value:,.2f}")
        print(f"Total return:    {((final_value - starting_value) / starting_value) * 100:.2f}%")
        print(f"CAGR:            {cagr * 100:.2f}%")
        print(f"Sharpe ratio:    {sharpe:.2f}")
        print(f"Sortino ratio:   {sortino:.2f}")
        print(f"Max drawdown:    {max_dd * 100:.2f}%")
        print(f"Win rate:        {win_rate * 100:.2f}%")
        print(f"Total trades:    {len(trades)}")
        print("-" * 50)
        status = "PASS" if bias_result["passed"] else "FAIL"
        print(f"Lookahead-bias check: {status} ({bias_result['checked_points']} points checked)")
        print("=" * 50)

    finally:
        session.close()


if __name__ == "__main__":
    main()

    