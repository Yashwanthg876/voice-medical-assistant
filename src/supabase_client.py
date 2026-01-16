from supabase import create_client
from dotenv import load_dotenv
import os

# -----------------------------------------
# Force-load .env from project root (Windows-safe)
# -----------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# -----------------------------------------
# Environment variables
# -----------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# -----------------------------------------
# Fail fast if anything is missing
# -----------------------------------------
if not SUPABASE_URL:
    raise Exception("SUPABASE_URL missing")

if not SUPABASE_ANON_KEY:
    raise Exception("SUPABASE_ANON_KEY missing")

if not SUPABASE_SERVICE_KEY:
    raise Exception("SUPABASE_SERVICE_KEY missing")

# -----------------------------------------
# Supabase clients
# -----------------------------------------
# Public client (auth, safe reads)
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Admin client (server-side writes, bypasses RLS)
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)