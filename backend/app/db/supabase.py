from supabase import create_client, Client
from backend.app.utils.config import config

def create_supabase_client():
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

supabase_client:Client = create_supabase_client()
