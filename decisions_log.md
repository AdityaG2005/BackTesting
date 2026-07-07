# Decisions Log

## Day 1

- **TimescaleDB over plain Postgres** — OHLCV data is inherently time-series; hypertables auto-partition by time, keeping date-range queries fast as row counts grow, while staying fully SQL/Postgres-compatible.
- **Docker for TimescaleDB** — avoids a messy manual Postgres+extension install on Windows; disposable and easy to reset if something breaks.
- **Composite primary key (id + timestamp) on Bar** — not a stylistic choice; TimescaleDB's create_hypertable() requires the partitioning column to be part of the primary/unique key.
- **Both backend and frontend on Render, instead of Render+Vercel split** — simpler troubleshooting with one dashboard while still learning deployment; free tier on both; can split later if needed since moving a static frontend to Vercel is low-effort.
- **yfinance over a paid/API-key-gated data source** — free, no signup friction, sufficient OHLCV coverage for AAPL/MSFT/SPY 2020-2024 for MVP purposes.
- **Only 3 tickers, 4 years of data for Day 1** — proves the ingestion pipeline works correctly before scaling up; easy to extend later by editing the TICKERS list and date range.

