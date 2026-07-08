# Decisions Log

## Day 1

- **TimescaleDB over plain Postgres** — OHLCV data is inherently time-series; hypertables auto-partition by time, keeping date-range queries fast as row counts grow, while staying fully SQL/Postgres-compatible.
- **Docker for TimescaleDB** — avoids a messy manual Postgres+extension install on Windows; disposable and easy to reset if something breaks.
- **Composite primary key (id + timestamp) on Bar** — not a stylistic choice; TimescaleDB's create_hypertable() requires the partitioning column to be part of the primary/unique key.
- **Both backend and frontend on Render, instead of Render+Vercel split** — simpler troubleshooting with one dashboard while still learning deployment; free tier on both; can split later if needed since moving a static frontend to Vercel is low-effort.
- **yfinance over a paid/API-key-gated data source** — free, no signup friction, sufficient OHLCV coverage for AAPL/MSFT/SPY 2020-2024 for MVP purposes.
- **Only 3 tickers, 4 years of data for Day 1** — proves the ingestion pipeline works correctly before scaling up; easy to extend later by editing the TICKERS list and date range.


## Day 2

- **Abstract Strategy base class using Python's ABC/abstractmethod** — chosen over a plain class + docstring convention, since ABC actually enforces at runtime that subclasses implement on_bar(). This matters especially for Day 5, where NLP-generated strategy code needs to reliably conform to the same interface.
- **on_bar(bar, history) signature, not a full-dataset-at-once approach** — deliberately limits each strategy to only see past data, enforcing point-in-time correctness (no lookahead bias) at the interface level, not just as a convention developers have to remember.
- **Signal as a dataclass with an Enum signal_type, not a dict with string values** — avoids typo/casing bugs (e.g. "Buy" vs "buy") and gets type-checking support from the editor.
- **RSI signals on every bar a threshold condition holds, not just the first crossing** — a deliberate simplification for Day 2; the simulation engine (Day 3) will decide how repeated signals translate into actual trade/position behavior, rather than baking that decision into the strategy itself.



