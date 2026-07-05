from app.db.session import Base, engine
from app.models import Instrument, Bar, BacktestRun

Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
