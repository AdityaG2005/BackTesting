from app.core.metrics import (
    calculate_daily_returns,
    calculate_sharpe,
    calculate_sortino,
    calculate_cagr,
    calculate_max_drawdown,
)


def main():
    # Toy equity curve: 5 days, hand-verifiable
    # Day 1: 100 -> Day 2: 110 (+10%) -> Day 3: 99 (-10%) -> Day 4: 108.9 (+10%) -> Day 5: 100.62 (-7.6%)
    equity_curve = [
        {"timestamp": "d1", "value": 100},
        {"timestamp": "d2", "value": 110},
        {"timestamp": "d3", "value": 99},
        {"timestamp": "d4", "value": 108.9},
        {"timestamp": "d5", "value": 100.62},
    ]

    print("--- Daily returns ---")
    returns = calculate_daily_returns(equity_curve)
    for r in returns:
        print(f"{r * 100:.2f}%")
    print("Expected: 10.00%, -10.00%, 10.00%, -7.60%")

    print("\n--- Max drawdown ---")
    max_dd = calculate_max_drawdown(equity_curve)
    print(f"Calculated: {max_dd * 100:.2f}%")
    print("Expected: peak=110 (day2), trough=99 (day3) -> (110-99)/110 = 10.00%")

    print("\n--- CAGR ---")
    # 100 -> 100.62 over 4 trading days (~0.0159 years if 252/yr)
    cagr = calculate_cagr(100, 100.62, num_trading_days=4)
    print(f"Calculated: {cagr * 100:.2f}%")
    print("Expected: small positive number (barely grew over ~4 trading days, annualized)")

    print("\n--- Sharpe (sanity check, not hand-verified exactly) ---")
    sharpe = calculate_sharpe(equity_curve)
    print(f"Calculated: {sharpe:.4f}")
    print("Expected: some finite number, not NaN/error, roughly near zero given mixed returns")

    print("\n--- Sortino ---")
    sortino = calculate_sortino(equity_curve)
    print(f"Calculated: {sortino:.4f}")
    print("Expected: some finite number, not NaN/error")


if __name__ == "__main__":
    main()

    