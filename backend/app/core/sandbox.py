import multiprocessing
from datetime import datetime, timezone


SAFE_BUILTINS = {
    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
    "enumerate": enumerate, "float": float, "int": int, "len": len,
    "list": list, "max": max, "min": min, "range": range, "round": round,
    "set": set, "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
    "zip": zip, "True": True, "False": False, "None": None,
    "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
    "isinstance": isinstance, "print": print,
    "__build_class__": __build_class__,
    "__name__": "generated_strategy",
}

SAFE_MODULES = {"math"}


def _safe_import(name, *args, **kwargs):
    if name in SAFE_MODULES:
        return __import__(name, *args, **kwargs)
    raise ImportError(f"Import of '{name}' is not allowed in strategy code")


class SimpleBar:
    """Plain, picklable stand-in for a SQLAlchemy Bar row, safe to pass across processes."""
    def __init__(self, timestamp, open_, high, low, close, volume, ticker):
        self.timestamp = timestamp
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.ticker = ticker


def _compile_strategy_class_sandboxed(code: str):
    from app.core.strategy import Strategy, Signal, SignalType

    restricted_builtins = dict(SAFE_BUILTINS)
    restricted_builtins["__import__"] = _safe_import

    namespace = {
        "__builtins__": restricted_builtins,
        "Strategy": Strategy,
        "Signal": Signal,
        "SignalType": SignalType,
    }

    exec(code, namespace)

    if "GeneratedStrategy" not in namespace:
        raise ValueError("Generated code did not define a class named GeneratedStrategy")

    return namespace["GeneratedStrategy"]


def _worker(code, strategy_params, bars_data, ticker, starting_cash, result_queue):
    try:
        from app.core.engine import BacktestEngine

        strategy_class = _compile_strategy_class_sandboxed(code)
        strategy = strategy_class(**strategy_params)

        bars = [
            SimpleBar(
                timestamp=b["timestamp"],
                open_=b["open"],
                high=b["high"],
                low=b["low"],
                close=b["close"],
                volume=b["volume"],
                ticker=ticker,
            )
            for b in bars_data
        ]

        engine = BacktestEngine(strategy, starting_cash=starting_cash)
        result = engine.run(bars, ticker=ticker)

        result_queue.put({"ok": True, "result": result})
    except Exception as e:
        result_queue.put({"ok": False, "error": str(e)})


def run_sandboxed_backtest(code, strategy_params, bars_data, ticker, starting_cash, timeout=10):
    """
    Runs a strategy's full backtest in an isolated subprocess with restricted
    builtins and a hard timeout. bars_data must be a list of plain dicts
    (not SQLAlchemy objects) so it can be pickled across the process boundary.
    """
    ctx = multiprocessing.get_context("spawn")
    result_queue = ctx.Queue()

    process = ctx.Process(
        target=_worker,
        args=(code, strategy_params, bars_data, ticker, starting_cash, result_queue),
    )
    process.start()
    process.join(timeout=timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return {"ok": False, "error": f"Strategy execution timed out after {timeout} seconds"}

    if result_queue.empty():
        return {"ok": False, "error": "Strategy process crashed without producing a result"}

    return result_queue.get()

