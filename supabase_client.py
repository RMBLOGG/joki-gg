from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from config import Config

options = ClientOptions(auto_refresh_token=False, persist_session=False)

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY, options=options)
supabase_admin: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY, options=options) if Config.SUPABASE_SERVICE_KEY else supabase
