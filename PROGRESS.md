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


## Day 3 — Event-driven simulation engine

**Built:**
- Order, Trade, Position dataclasses (app/core/portfolio.py) — Trade has is_open and pnl as computed properties
- OrderMatcher (app/core/order_matcher.py) — slippage (0.1%) always works against the trader, commission (0.1%) on trade value
- Portfolio (app/core/portfolio.py) — tracks cash/position, only acts on BUY if flat / SELL if holding, all-in position sizing, maintains trade log
- BacktestEngine (app/core/engine.py) — core event loop; replays bars in time order, fills signals at NEXT bar's open (not current bar), builds equity curve day by day
- End-to-end test (test_engine.py): MovingAverageCrossover on AAPL 2020-2024 → $10,000 to $18,705.26 (87.05% return), 11 trades, 1 left open at data end

**Left for later days:**
- Position sizing is "all-in" — no fractional/risk-based sizing yet (planned, matches project plan's stated requirement)
- Long-only, single position at a time — no shorting, no scaling in/out
- No error handling if a strategy throws mid-replay
- No way yet to judge if 87% return is actually "good" — no Sharpe, drawdown, or benchmark comparison (Day 4)


## Day 4 — Performance metrics + lookahead-bias validation

**Built:**
- metrics.py: calculate_sharpe, calculate_sortino, calculate_cagr, calculate_max_drawdown, calculate_win_rate
- Toy-data sanity test (test_metrics_sanity.py) — verified daily returns and max drawdown by hand; caught a real CAGR bug (was using 365.25 calendar days instead of 252 trading days)
- Real metrics test (test_metrics_real.py) — ran full metric suite on Day 3's AAPL MA Crossover result:
  CAGR 16.98%, Sharpe 0.84, Sortino 0.68, Max drawdown 23.12%, Win rate 60%
- Lookahead-bias regression test (bias_check.py) — compares strategy signal on full vs. truncated data at the same check point; both MovingAverageCrossover and RSIMeanReversion pass
- Combined report script (generate_report.py) — metrics + bias check status in one readable output

**Left for later days:**
- Bias check only samples 4 points (25/50/75/last), not exhaustive across every bar
- No NLP strategy layer, no async API, no frontend dashboard yet (Days 5-6)
- Report is currently script/terminal output only — not exposed via API or UI



