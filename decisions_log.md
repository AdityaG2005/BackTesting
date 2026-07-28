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




## Day 4

- **Sortino only penalizes downside returns in its denominator, while Sharpe penalizes all volatility** — deliberate distinction per each metric's definition, not an inconsistency. A lower Sortino than Sharpe on the same strategy is a real signal that its volatility skews toward downside moves specifically.
- **CAGR uses 252 trading days, not 365.25 calendar days** — equity_curve entries are per trading day (from bar-by-bar replay), so years must be computed as num_trading_days / 252. Originally implemented with 365.25 (a real bug), caught via toy-data sanity check before trusting it on real results.
- **Toy-data sanity checks run before real-data tests** — per the project's own stated principle: real data makes a plausible-but-wrong number hard to catch by eye; a hand-computed 5-day series makes correctness verifiable exactly, not just "looks about right."
- **Lookahead-bias check samples 4 spread-out points (25/50/75/last), not every bar** — pragmatic MVP tradeoff; a real bug would typically show up consistently rather than at only isolated bars, so sampling is a reasonable sanity check without being a fully exhaustive proof.
- **Bias check uses a strategy_factory (fresh instance per run) rather than reusing one strategy object** — eliminates any risk of leftover internal state contaminating the full-vs-truncated comparison.




## Day 5

- **Gemini (primary) + Groq (fallback) instead of Anthropic** — both offer genuinely free tiers with no card required, unlike Anthropic at the time of building this. Automatic fallback on failure was tested for real (Gemini's model deprecation triggered it), not just designed hypothetically.
- **include=["app.core.tasks"] in celery_app.py** — required because Celery only registers @celery_app.task-decorated functions if the module defining them is actually imported; without this, the worker silently has an empty task list.
- **--pool=solo for the Celery worker** — Windows-specific workaround since the default prefork pool relies on Unix-only os.fork(). Known tradeoff: no task concurrency in dev; production (likely Linux) would use a different pool.
- **Two-gate + bias-check validation for NLP-generated code, not just a syntax check** — a syntactically valid strategy can still be logically wrong (e.g. accidentally referencing future data). Reusing the Day 4 lookahead-bias check against real market data catches behavioral bugs a syntax check cannot.
- **exec() restricted namespace is NOT true sandboxing** — it limits which names are pre-available (Strategy/Signal/SignalType only) but does not prevent imports, filesystem access, or network calls. True sandboxing (restricted imports, timeouts, no filesystem/network) is deliberately deferred to Day 7, applied to both NLP-generated and user-submitted code paths.
- **python -m pip / python -m uvicorn / python -m celery instead of direct .exe calls** — Windows Smart App Control blocked the standalone executables; routing through python.exe (already trusted) sidesteps this without disabling a security feature that cannot be re-enabled once turned off.





- Switched from local TimescaleDB (Docker) to Render's managed PostgreSQL for the deployed backend — Render backend couldn't reach a database running on a local machine. Matches the project plan's own stated fallback ("if TimescaleDB isn't available on the free tier of your chosen host, plain Postgres is a fine fallback for the MVP demo"). No application code changed; only the DATABASE_URL differs between local (TimescaleDB via Docker) and deployed (Render Postgres) environments. Local development can still use TimescaleDB/hypertables since docker-compose is unaffected.





- Render's free PostgreSQL tier expires ~30 days after creation (created [today's date], expires Aug 26, 2026) — will need to either recreate a fresh free instance and re-migrate data, or upgrade to a paid tier, before that date. Noted here as a known operational limitation of the free-tier hosting choice.





- Render free tier spins down web services after ~15 min inactivity; first request after idle takes ~10-50s to "wake up." Known, accepted limitation of free-tier hosting for a personal/demo project — not a code issue.





