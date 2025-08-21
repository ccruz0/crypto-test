# insert_and_read_signals.py
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import json

# 1) Cargar SUPABASE_URL y SUPABASE_KEY desde .env (si existe)
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_KEY en tu entorno/.env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2) Insertar una fila dummy usando SOLO columnas reales de la tabla
payload = {
    "signal_type": "test_signal",
    "params_json": {"param1": "value1", "param2": 123},
    "status": "pending",
    # created_at es timestamptz, enviamos ISO UTC
    "created_at": datetime.now(timezone.utc).isoformat()
}
print("Insertando fila dummy…")
insert_res = supabase.table("signals").insert(payload).execute()
print("Insert OK:", insert_res.data)

# 3) Leer la fila más reciente y mostrar columnas detectadas
sel_res = (
    supabase.table("signals")
    .select("*")
    .order("created_at", desc=True)
    .limit(1)
    .execute()
)
rows = sel_res.data or []
cols = list(rows[0].keys()) if rows else []
print("Última fila:", json.dumps(rows, indent=2, ensure_ascii=False))
print("Columnas:", cols)

# 4) (Opcional) Contar filas en la tabla
cnt_res = supabase.table("signals").select("id", count="exact").execute()
print("Total filas en signals:", cnt_res.count)