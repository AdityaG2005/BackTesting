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


## Day 3

- **Fill at next bar's open, never current bar's close** — the core anti-lookahead-bias mechanism. A signal generated using bar N's data can only realistically be acted on starting bar N+1, since in real life you wouldn't have known about the signal until bar N fully closed.
- **Slippage always works against the trader (buy higher, sell lower)** — deliberately pessimistic/conservative assumption; better to slightly understate simulated returns than overstate them with unrealistically perfect fills.
- **All-in position sizing for now** — chosen to isolate and verify the fill/tracking mechanism's correctness before adding a second variable (how much to risk per trade). A configurable position sizer is a planned next step, not a missed requirement.
- **is_open and pnl on Trade implemented as @property, not stored fields** — avoids the two ever going out of sync with the actual source of truth (exit_timestamp/exit_price).
- **Each BacktestEngine instance owns its own Portfolio/OrderMatcher** — no shared/global state, so multiple backtests could run concurrently without interfering with each other later.
- **Raw return % alone isn't a valid success metric** — 87% return on paper means nothing without knowing the risk taken to get there (Sharpe), the worst drawdown experienced, or how it compares to a passive buy-and-hold baseline. Day 4 exists specifically to answer "was this actually good," not just "did it make money."






