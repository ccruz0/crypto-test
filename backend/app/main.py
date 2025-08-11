import os
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import psycopg2
from psycopg2.pool import SimpleConnectionPool

# ---------- Config ----------
DB_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL (o SUPABASE_DB_URL) no está definido")

app = FastAPI(title="Crypto Bot Starter Kit v0")

pool: SimpleConnectionPool | None = None


# ---------- Modelos ----------
class Signal(BaseModel):
    symbol: str
    side: str          # "buy" | "sell"
    price: float
    confidence: Optional[float] = None
    note: Optional[str] = None
    ts: Optional[datetime] = None


# ---------- Helpers ----------
def db_conn():
    """Obtiene una conexión del pool como context manager."""
    assert pool is not None
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def exec_query(sql: str, params: tuple | None = None, fetch: str | None = None):
    """Ejecuta una consulta de forma segura y opcionalmente recupera resultados."""
    # pequeño wrapper práctico
    for conn in db_conn():
        with conn, conn.cursor() as cur:
            cur.execute(sql, params or ())
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()
            return None


# ---------- Ciclo de vida ----------
@app.on_event("startup")
def on_startup():
    global pool
    # Pool de conexiones (ajusta maxconn si lo necesitas)
    pool = SimpleConnectionPool(minconn=1, maxconn=5, dsn=DB_URL)

    # Extensión y tabla (id UUID + timestamp)
    exec_query("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    exec_query(
        """
        CREATE TABLE IF NOT EXISTS signals (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            symbol TEXT,
            side TEXT,
            price DOUBLE PRECISION,
            confidence DOUBLE PRECISION,
            note TEXT,
            ts TIMESTAMPTZ DEFAULT NOW()
        );
        """
    )


@app.on_event("shutdown")
def on_shutdown():
    global pool
    if pool:
        pool.closeall()
        pool = None


# ---------- Rutas básicas ----------
@app.get("/health")
def health():
    return {"status": "ok", "env": os.getenv("RENDER", "render")}


@app.get("/summary")
def summary():
    return {"pnl": {"daily": 0, "weekly": 0}, "open_orders": [], "recent_fills": []}


# ---------- API de señales ----------
@app.get("/signals", response_model=List[Signal])
def get_signals():
    rows = exec_query(
        "SELECT symbol, side, price, confidence, note, ts FROM signals ORDER BY ts DESC",
        fetch="all",
    ) or []
    return [
        Signal(
            symbol=r[0], side=r[1], price=r[2],
            confidence=r[3], note=r[4], ts=r[5]
        )
        for r in rows
    ]


@app.post("/signals", response_model=Signal)
def add_signal(signal: Signal):
    if signal.side not in ("buy", "sell"):
        raise HTTPException(status_code=400, detail="side must be 'buy' or 'sell'")

    saved = exec_query(
        """
        INSERT INTO signals (symbol, side, price, confidence, note, ts)
        VALUES (%s, %s, %s, %s, %s, COALESCE(%s, NOW()))
        RETURNING symbol, side, price, confidence, note, ts
        """,
        (signal.symbol, signal.side, signal.price,
         signal.confidence, signal.note, signal.ts),
        fetch="one",
    )
    return Signal(
        symbol=saved[0], side=saved[1], price=saved[2],
        confidence=saved[3], note=saved[4], ts=saved[5]
    )
