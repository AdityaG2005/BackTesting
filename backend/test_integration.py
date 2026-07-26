import time
import requests

BASE_URL = "http://localhost:8000"


def submit_backtest(strategy_id, ticker, start_date, end_date, starting_cash=10000, strategy_params=None):
    response = requests.post(f"{BASE_URL}/backtest", json={
        "strategy_id": strategy_id,
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "starting_cash": starting_cash,
        "strategy_params": strategy_params or {}
    })
    response.raise_for_status()
    return response.json()


def poll_backtest(backtest_id, timeout=30, interval=1):
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(f"{BASE_URL}/backtest/{backtest_id}")
        response.raise_for_status()
        data = response.json()

        if data["status"] in ("done", "failed"):
            return data

        print(f"  status: {data['status']}... waiting")
        time.sleep(interval)

    raise TimeoutError(f"Backtest {backtest_id} did not complete within {timeout}s")


def main():
    print("--- Submitting backtest ---")
    submission = submit_backtest(
        strategy_id="rsi_mean_reversion",
        ticker="MSFT",
        start_date="2020-01-01",
        end_date="2024-01-01"
    )
    backtest_id = submission["id"]
    print(f"Submitted. ID={backtest_id}, initial status={submission['status']}")

    print("\n--- Polling for completion ---")
    result = poll_backtest(backtest_id)

    print(f"\nFinal status: {result['status']}")
    if result["status"] == "done":
        results = result["config"]["results"]
        print(f"Final value:   ${results['final_value']:,.2f}")
        print(f"CAGR:          {results['cagr'] * 100:.2f}%")
        print(f"Sharpe:        {results['sharpe']:.2f}")
        print(f"Max drawdown:  {results['max_drawdown'] * 100:.2f}%")
        print(f"Win rate:      {results['win_rate'] * 100:.2f}%")
        print(f"Total trades:  {results['total_trades']}")
    else:
        print("Backtest failed — check Celery worker logs.")


if __name__ == "__main__":
    main()