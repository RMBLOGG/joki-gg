import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "jokigg-secret-2024")

    SUPABASE_URL = "https://mafnnqttvkdgqqxczqyt.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1hZm5ucXR0dmtkZ3FxeGN6cXl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4NzQyMDEsImV4cCI6MjA4NzQ1MDIwMX0.YRh1oWVKnn4tyQNRbcPhlSyvr7V_1LseWN7VjcImb-Y"
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

    CLOUDINARY_CLOUD_NAME = "dzfkklsza"
    CLOUDINARY_API_KEY = "588474134734416"
    CLOUDINARY_API_SECRET = "9c12YJe5rZSYSg7zROQuvmVZ7mg"

    COMMISSION_RATE = 0.15  # 15% komisi platform
