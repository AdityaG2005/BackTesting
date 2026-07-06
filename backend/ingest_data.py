import pandas as pd
import yfinance as yf
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.models import Instrument, Bar

TICKERS = ["AAPL", "MSFT", "SPY"]

def get_or_create_instrument(session, ticker):
    instrument = session.query(Instrument).filter_by(ticker=ticker).first()
    if instrument:
        return instrument

    info = yf.Ticker(ticker)
    instrument = Instrument(
        ticker=ticker,
        name=info.info.get("longName", ticker),
        exchange=info.info.get("exchange", "UNKNOWN")
    )
    session.add(instrument)
    session.commit()
    session.refresh(instrument)
    return instrument

def ingest_ticker(session, ticker):
    print(f"Fetching {ticker}...")
    instrument = get_or_create_instrument(session, ticker)

    data = yf.download(ticker, start="2020-01-01", end="2024-01-01", progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    bars = []
    for date, row in data.iterrows():
        bar = Bar(
            instrument_id=instrument.id,
            timestamp=date.to_pydatetime().replace(tzinfo=timezone.utc),
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=float(row["Volume"])
        )
        bars.append(bar)

    session.bulk_save_objects(bars)
    session.commit()
    print(f"Inserted {len(bars)} bars for {ticker}")

def main():
    session = SessionLocal()
    try:
        for ticker in TICKERS:
            ingest_ticker(session, ticker)
    finally:
        session.close()

if __name__ == "__main__":
    main()

    