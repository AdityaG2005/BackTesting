from sqlalchemy import Column, Integer, String
from app.db.session import Base

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    exchange = Column(String, nullable=True)
    