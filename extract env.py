from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()  # loads SUPABASE_URL and SUPABASE_KEY from .env if present

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY env vars")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Insertar una fila de prueba en la tabla 'signals'
supabase.table("signals").insert({
    "test_column": "test value",
    "created_at": "2025-08-11T12:00:00Z"
}).execute()

print("Fila dummy insertada")

resp = supabase.table("signals").select("*").limit(1).execute()
rows = resp.data or []
cols = list(rows[0].keys()) if rows else []
print("Columnas:", cols)
resp = supabase.table("signals").select("*").limit(1).execute()
print(resp)