from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.db.session import Base

class Bar(Base):
    __tablename__ = "bars"

    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    