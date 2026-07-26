from datetime import datetime

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import Instrument, Bar, BacktestRun
from app.core.strategies.moving_average_crossover import MovingAverageCrossover
from app.core.strategies.rsi_mean_reversion import RSIMeanReversion
from app.core.engine import BacktestEngine
from app.core.nlp_strategy import compile_strategy_class
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


@celery_app.task
def run_backtest_task(backtest_run_id: int):
    session = SessionLocal()
    try:
        run = session.query(BacktestRun).filter_by(id=backtest_run_id).first()
        if run is None:
            return

        run.status = "running"
        session.commit()

        config = run.config

        if config.get("strategy_code"):
            try:
                strategy_class = compile_strategy_class(config["strategy_code"])
            except Exception:
                run.status = "failed"
                session.commit()
                return
        else:
            strategy_class = STRATEGY_MAP.get(config["strategy_id"])
            if strategy_class is None:
                run.status = "failed"
                session.commit()
                return

        strategy_params = config.get("strategy_params", {})
        strategy = strategy_class(**strategy_params)

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

        engine = BacktestEngine(strategy, starting_cash=config["starting_cash"])
        result = engine.run(bars, ticker=config["ticker"])

        equity_curve = result["equity_curve"]
        trades = result["trades"]

        sharpe = calculate_sharpe(equity_curve)
        sortino = calculate_sortino(equity_curve)
        cagr = calculate_cagr(result["starting_cash"], result["final_value"], len(equity_curve))
        max_dd = calculate_max_drawdown(equity_curve)
        win_rate = calculate_win_rate(trades)

        run.status = "done"
        run.config = {
            **config,
            "results": {
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
            }
        }
        session.commit()

    except Exception as e:
        run.status = "failed"
        session.commit()
    finally:
        session.close()