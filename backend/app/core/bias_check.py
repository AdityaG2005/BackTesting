from app.core.strategy import SignalType


def check_lookahead_bias(strategy_factory, bars, ticker, check_points=None):
    """
    strategy_factory: a function that returns a FRESH strategy instance
                       (so each run starts with zero internal state)
    bars: full list of bars, in time order
    check_points: list of bar indices to test; defaults to a spread across the dataset
    """
    if check_points is None:
        n = len(bars)
        check_points = [n // 4, n // 2, (3 * n) // 4, n - 1]

    mismatches = []

    for check_point in check_points:
        if check_point < 1:
            continue

        full_signal = _get_signal_at(strategy_factory(), bars, ticker, check_point)
        truncated_bars = bars[:check_point + 1]
        truncated_signal = _get_signal_at(strategy_factory(), truncated_bars, ticker, check_point)

        if full_signal.signal_type != truncated_signal.signal_type:
            mismatches.append({
                "index": check_point,
                "timestamp": bars[check_point].timestamp,
                "full_signal": full_signal.signal_type,
                "truncated_signal": truncated_signal.signal_type
            })

    passed = len(mismatches) == 0
    return {
        "passed": passed,
        "checked_points": len(check_points),
        "mismatches": mismatches
    }


def _get_signal_at(strategy, bars, ticker, target_index):
    history = []
    signal = None
    for i, bar in enumerate(bars):
        bar.ticker = ticker
        signal = strategy.on_bar(bar, history)
        history.append(bar)
        if i == target_index:
            break
    return signal

