import streamlit as st
from supabase import create_client, Client
import pandas as pd
from config.settings import settings

# Initialize Supabase client
@st.cache_resource
def get_supabase_client() -> Client:
    # Use environment variables or default settings
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    return create_client(url, key)

@st.cache_data(ttl=600)
def fetch_transactions() -> pd.DataFrame:
    """
    Fetches all transactions from Supabase.
    Caches the result for 10 minutes (600 seconds) to improve performance.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("transactions").select("*").execute()
        
        # Convert to DataFrame
        data = response.data
        if not data:
            # Return empty DataFrame with expected columns if no data
            return pd.DataFrame(columns=["id", "date", "type", "category", "amount", "desc", "status"])
            
        df = pd.DataFrame(data)
        
        # Ensure date column is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
        # Ensure amount column is numeric
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        st.error(f"Error fetching data from Supabase: {str(e)}")
        # Return empty df as fallback
        return pd.DataFrame(columns=["id", "date", "type", "category", "amount", "desc", "status"])
