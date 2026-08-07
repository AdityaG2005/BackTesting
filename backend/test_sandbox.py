from datetime import datetime, timezone
from app.core.sandbox import run_sandboxed_backtest

# Tiny synthetic dataset - no DB needed for this test
bars_data = [
    {"timestamp": datetime(2024, 1, i, tzinfo=timezone.utc), "open": 100 + i, "high": 101 + i, "low": 99 + i, "close": 100 + i, "volume": 1000}
    for i in range(1, 10)
]

GOOD_CODE = """
class GeneratedStrategy(Strategy):
    def on_bar(self, bar, history) -> Signal:
        if not history:
            return Signal(signal_type=SignalType.HOLD, timestamp=bar.timestamp, ticker=bar.ticker, reason="no history")
        if bar.close > history[-1].close:
            return Signal(signal_type=SignalType.BUY, timestamp=bar.timestamp, ticker=bar.ticker, reason="up")
        return Signal(signal_type=SignalType.HOLD, timestamp=bar.timestamp, ticker=bar.ticker, reason="flat/down")
"""

MALICIOUS_IMPORT_CODE = """
import os
class GeneratedStrategy(Strategy):
    def on_bar(self, bar, history) -> Signal:
        os.system("echo this should never run")
        return Signal(signal_type=SignalType.HOLD, timestamp=bar.timestamp, ticker=bar.ticker, reason="x")
"""

INFINITE_LOOP_CODE = """
class GeneratedStrategy(Strategy):
    def on_bar(self, bar, history) -> Signal:
        while True:
            pass
"""


def run_test(name, code):
    print(f"\n--- {name} ---")
    result = run_sandboxed_backtest(
        code=code,
        strategy_params={},
        bars_data=bars_data,
        ticker="TEST",
        starting_cash=10000,
        timeout=5,
    )
    if result["ok"]:
        print(f"OK. Final value: {result['result']['final_value']}")
    else:
        print(f"Failed as expected (or unexpectedly): {result['error']}")


if __name__ == "__main__":
    run_test("Valid strategy (should succeed)", GOOD_CODE)
    run_test("Malicious import (should be blocked)", MALICIOUS_IMPORT_CODE)
    run_test("Infinite loop (should time out after 5s)", INFINITE_LOOP_CODE)

    