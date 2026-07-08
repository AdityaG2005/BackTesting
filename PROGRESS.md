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



## Day 2 — Strategy interface + preset strategies

**Built:**
- Abstract strategy interface (app/core/strategy.py): SignalType enum, Signal dataclass, Strategy ABC with on_bar() as the required method
- Two concrete strategies: MovingAverageCrossover (20/50-day), RSIMeanReversion (14-day period, 30/70 thresholds)
- Script-level test (test_strategies.py): ran both against real AAPL data (2020-2024) from the DB
  - MA Crossover: 21 signals (sparse, event-based)
  - RSI Mean Reversion: 276 signals (frequent, condition-based)

**Left for later days:**
- No order matching / position tracking yet — signals are generated but nothing "trades" on them (Day 3)
- No error handling around on_bar() calls if a strategy throws mid-replay
- RSI fires every day a threshold condition holds, not just on first crossing — engine will need to decide how to interpret repeated signals (Day 3)

