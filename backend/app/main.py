# backend/app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# --- Supabase client ---
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Faltan SUPABASE_URL / SUPABASE_KEY en .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Crypto Bot Starter Kit v0")

# CORS para permitir que el index.html cargado en el navegador consulte al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # si quieres restringir, pon tu dominio aquí
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Modelos ----------
class Signal(BaseModel):
    symbol: str
    side: str
    price: float
    confidence: Optional[float] = None
    note: Optional[str] = None
    ts: Optional[str] = None
    created_at: Optional[str] = None

# ---------- Rutas existentes simples ----------
@app.get("/health")
def health():
    return {"status": "ok", "env": os.getenv("RENDER", "false") == "true"}

@app.get("/summary")
def summary():
    return {"pnl": {"daily": 0, "weekly": 0}, "open_orders": [], "recent_fills": []}

@app.get("/signals", response_model=List[Signal])
def get_signals(limit: int = 50):
    try:
        resp = (
            supabase.table("signals")
            .select("symbol,side,price,confidence,note,ts,created_at")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signals", response_model=Signal)
def add_signal(signal: Signal):
    if signal.side not in ("buy", "sell"):
        raise HTTPException(status_code=400, detail="side must be 'buy' or 'sell'")
    try:
        # Si no viene ts, lo deja nulo; Supabase rellenará created_at por DEFAULT now()
        payload = signal.model_dump(exclude_none=True)
        resp = supabase.table("signals").insert(payload).select("*").execute()
        if not resp.data:
            raise RuntimeError("Insert returned no data")
        row = resp.data[0]
        return Signal(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- NUEVO: /signals/live ----------
@app.get("/signals/live")
def signals_live(
    symbols: Optional[str] = Query(None, description="Lista separada por comas, p.ej. BTC,ETH,SOL"),
    limit: int = Query(50, ge=1, le=500)
):
    """
    Devuelve las últimas señales desde Supabase.
    - Si 'symbols' viene, filtra por esos símbolos (ej.: BTC,ETH,SOL).
    - Ordena por created_at desc y limita 'limit'.
    """
    try:
        q = supabase.table("signals").select("symbol,side,price,confidence,note,ts,created_at")
        if symbols:
            wanted = [s.strip().upper() for s in symbols.split(",") if s.strip()]
            if wanted:
                q = q.in_("symbol", wanted)
        resp = q.order("created_at", desc=True).limit(limit).execute()
        return {"rows": resp.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))