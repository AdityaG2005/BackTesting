from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime, timezone
from app.db.session import Base

class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True)
    config = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    