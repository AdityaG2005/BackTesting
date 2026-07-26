from fastapi import FastAPI
from app.api.strategies import router as strategies_router
from app.api.backtest import router as backtest_router

app = FastAPI(title="Backtesting Engine")

app.include_router(strategies_router)
app.include_router(backtest_router)

@app.get("/health")
def health():
    return {"status": "ok"}