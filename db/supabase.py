from supabase import create_client
from config import config

def create_supabase_client():
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

supabase = create_supabase_client()