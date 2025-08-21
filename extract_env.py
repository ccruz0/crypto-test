from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()  # lee SUPABASE_URL y SUPABASE_KEY del .env

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
assert SUPABASE_URL and SUPABASE_KEY, "Faltan SUPABASE_URL/SUPABASE_KEY en .env"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# cuántas filas quieres
LIMIT = 10

# Trae las últimas N por fecha de creación
resp = (
    supabase.table("signals")
    .select("symbol,side,price,confidence,note,ts,created_at")
    .order("created_at", desc=True)
    .limit(LIMIT)
    .execute()
)

print(resp.data)