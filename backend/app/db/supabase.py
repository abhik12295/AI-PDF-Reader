import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_KEY = os.getenv("JWT_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY:", SUPABASE_KEY[:10] + "********")  # Masked for security

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Check .env file.")

# Create Supabase client
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)