import os
from dotenv import load_dotenv

# Load environment variables (e.g. from .env file if available)
load_dotenv()

class Settings:
    # Supabase Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://your-supabase-url.supabase.co")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "your-supabase-anon-key")

    # App Settings
    APP_NAME = "Karang Taruna Digital"
    PAGE_TITLE = "AI Financial Dashboard"
    PAGE_ICON = "📈"

    # Model Configuration
    MODEL_PATH = os.path.join("models", "model_lstm.keras")
    SCALER_PATH = os.path.join("models", "scaler.pkl")

settings = Settings()
