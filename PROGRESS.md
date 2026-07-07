# Progress

## Day 1 — Data layer + project skeleton

**Built:**
- FastAPI skeleton with `/health` route, folder structure (app/core, app/models, app/api, app/db)
- Virtual environment + dependencies (fastapi, sqlalchemy, psycopg2-binary, yfinance, etc.)
- SQLAlchemy models: Instrument, Bar, BacktestRun
- TimescaleDB running via Docker (timescale/timescaledb:latest-pg16), bars table converted to hypertable
- Data ingestion via yfinance: AAPL, MSFT, SPY (2020-2024), 3018 bars total
- Deployed backend (FastAPI) to Render as a Web Service
- Deployed frontend (placeholder React/Vite) to Render as a Static Site
- Confirmed auto-deploy on push to main for both services

**Left for later days:**
- Strategy interface / order matcher abstractions
- Actual backtest simulation engine (Day 3+)
- BacktestRun table currently empty/unused
- No uniqueness constraint on (instrument_id, timestamp) in bars — duplicate ingestion risk
- More tickers / longer date ranges (currently only 3 tickers, 2020-2024)

**Live URLs:**
- Backend: https://backtesting-backend-66at.onrender.com
- Frontend: https://backtesting-frontend-by65.onrender.com
- Repo: https://github.com/AdityaG2005/BackTesting

