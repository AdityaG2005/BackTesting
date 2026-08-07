from datetime import datetime

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import Instrument, Bar, BacktestRun
from app.core.strategies.moving_average_crossover import MovingAverageCrossover
from app.core.strategies.rsi_mean_reversion import RSIMeanReversion
from app.core.engine import BacktestEngine
from app.core.sandbox import run_sandboxed_backtest
from app.core.metrics import (
    calculate_sharpe,
    calculate_sortino,
    calculate_cagr,
    calculate_max_drawdown,
    calculate_win_rate,
)

STRATEGY_MAP = {
    "moving_average_crossover": MovingAverageCrossover,
    "rsi_mean_reversion": RSIMeanReversion,
}


def _serialize_trades(trades):
    serialized = []
    for t in trades:
        serialized.append({
            "entry_timestamp": t.entry_timestamp.isoformat() if t.entry_timestamp else None,
            "exit_timestamp": t.exit_timestamp.isoformat() if t.exit_timestamp else None,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "quantity": t.quantity,
            "is_open": t.is_open,
            "pnl": t.pnl,
        })
    return serialized


def _bars_to_dicts(bars):
    return [
        {
            "timestamp": b.timestamp,
            "open": b.open,
            "high": b.high,
            "low": b.low,
            "close": b.close,
            "volume": b.volume,
        }
        for b in bars
    ]


def _build_results(result, equity_curve, trades):
    sharpe = calculate_sharpe(equity_curve)
    sortino = calculate_sortino(equity_curve)
    cagr = calculate_cagr(result["starting_cash"], result["final_value"], len(equity_curve))
    max_dd = calculate_max_drawdown(equity_curve)
    win_rate = calculate_win_rate(trades)

    return {
        "final_value": result["final_value"],
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "total_trades": len(trades),
        "equity_curve": [
            {"timestamp": point["timestamp"].isoformat(), "value": point["value"]}
            for point in equity_curve
        ],
        "trades": _serialize_trades(trades),
    }


def _execute_backtest(session, run):
    run.status = "running"
    session.commit()

    config = run.config

    instrument = session.query(Instrument).filter_by(ticker=config["ticker"]).first()
    if instrument is None:
        run.status = "failed"
        session.commit()
        return

    bars = (
        session.query(Bar)
        .filter_by(instrument_id=instrument.id)
        .order_by(Bar.timestamp)
        .all()
    )

    strategy_params = config.get("strategy_params", {})

    if config.get("strategy_code"):
        bars_data = _bars_to_dicts(bars)
        sandbox_result = run_sandboxed_backtest(
            code=config["strategy_code"],
            strategy_params=strategy_params,
            bars_data=bars_data,
            ticker=config["ticker"],
            starting_cash=config["starting_cash"],
            timeout=10,
        )

        if not sandbox_result["ok"]:
            run.status = "failed"
            run.config = {**config, "error": sandbox_result["error"]}
            session.commit()
            return

        result = sandbox_result["result"]

    else:
        strategy_class = STRATEGY_MAP.get(config["strategy_id"])
        if strategy_class is None:
            run.status = "failed"
            session.commit()
            return

        strategy = strategy_class(**strategy_params)
        engine = BacktestEngine(strategy, starting_cash=config["starting_cash"])
        result = engine.run(bars, ticker=config["ticker"])

    equity_curve = result["equity_curve"]
    trades = result["trades"]

    run.status = "done"
    run.config = {
        **config,
        "results": _build_results(result, equity_curve, trades),
    }
    session.commit()


@celery_app.task
def run_backtest_task(backtest_run_id: int):
    session = SessionLocal()
    try:
        run = session.query(BacktestRun).filter_by(id=backtest_run_id).first()
        if run is None:
            return
        _execute_backtest(session, run)
    except Exception:
        run.status = "failed"
        session.commit()
    finally:
        session.close()


def run_backtest_sync(backtest_run_id: int):
    """
    Synchronous fallback for deployment environments without a persistent
    background worker (e.g. Render free tier). Runs the exact same logic
    as run_backtest_task, just in-process and blocking. Used because this
    project's backtests complete in ~1-2 seconds, making a queue
    unnecessary for demo-scale deployment.
    """
    session = SessionLocal()
    try:
        run = session.query(BacktestRun).filter_by(id=backtest_run_id).first()
        if run is None:
            return
        _execute_backtest(session, run)
    except Exception:
        run.status = "failed"
        session.commit()
    finally:
        session.close()

        