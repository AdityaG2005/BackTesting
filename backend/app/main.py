from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.strategies import router as strategies_router
from app.api.backtest import router as backtest_router

app = FastAPI(title="Backtesting Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://backtesting-frontend-by65.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(strategies_router)
app.include_router(backtest_router)


@app.get("/health")
def health():
    return {"status": "ok"}
