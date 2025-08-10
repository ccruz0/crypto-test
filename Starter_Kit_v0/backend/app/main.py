from fastapi import FastAPI
from .config import settings

app = FastAPI(title="Crypto Bot Starter Kit v0")

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}

@app.get("/summary")
def summary():
    return {"pnl": {"daily": 0, "weekly": 0}, "open_orders": [], "recent_fills": []}

@app.get("/signals")
def signals():
    return []
