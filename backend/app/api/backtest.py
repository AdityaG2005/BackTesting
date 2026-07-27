from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.session import SessionLocal
from app.models import BacktestRun
from app.core.tasks import run_backtest_task, run_backtest_sync

router = APIRouter()


class BacktestConfig(BaseModel):
    strategy_id: str
    ticker: str
    start_date: str
    end_date: str
    starting_cash: float = 10000
    strategy_params: dict = {}
    strategy_code: Optional[str] = None


@router.post("/backtest")
def submit_backtest(config: BacktestConfig):
    session = SessionLocal()
    try:
        run = BacktestRun(
            config=config.model_dump(),
            status="pending"
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        run_backtest_sync(run.id)

        session.refresh(run)
        return {"id": run.id, "status": run.status}
    finally:
        session.close()


@router.get("/backtest/{backtest_id}")
def get_backtest(backtest_id: int):
    session = SessionLocal()
    try:
        run = session.query(BacktestRun).filter_by(id=backtest_id).first()

        if run is None:
            raise HTTPException(status_code=404, detail="Backtest run not found")

        return {
            "id": run.id,
            "status": run.status,
            "config": run.config
        }
    finally:
        session.close()