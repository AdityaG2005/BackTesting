from fastapi import FastAPI

app = FastAPI(title="Backtesting Engine")

@app.get("/health")
def health():
    return {"status": "ok"}
