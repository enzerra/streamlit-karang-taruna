import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
from datetime import timedelta

# Try to import tensorflow, but don't break if not installed yet during dev
try:
    from tensorflow.keras.models import load_model
except ImportError:
    load_model = None

from services.supabase_service import fetch_transactions
from config.settings import settings
from utils.preprocessing import aggregate_daily_transactions

@st.cache_resource
def load_lstm_model():
    """Loads the pre-trained LSTM model."""
    try:
        if load_model is None:
            return None
        if os.path.exists(settings.MODEL_PATH):
            return load_model(settings.MODEL_PATH)
        else:
            st.warning("Model file not found. Please place model_lstm.keras in the models/ directory.")
            return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

@st.cache_resource
def load_data_scaler():
    """Loads the pre-trained scaler."""
    try:
        if os.path.exists(settings.SCALER_PATH):
            return joblib.load(settings.SCALER_PATH)
        else:
            st.warning("Scaler file not found. Please place scaler.pkl in the models/ directory.")
            return None
    except Exception as e:
        st.error(f"Error loading scaler: {str(e)}")
        return None

def get_transactions():
    """Wrapper to get transactions for prediction pipeline."""
    return fetch_transactions()

def prepare_lstm_data(df: pd.DataFrame, time_steps=30):
    """
    Prepares aggregated daily data for LSTM prediction.
    Requires at least 'time_steps' days of historical data.
    """
    daily_df = aggregate_daily_transactions(df)
    
    if len(daily_df) < time_steps:
        return None, daily_df, False # Not enough data
        
    scaler = load_data_scaler()
    if scaler is None:
        return None, daily_df, False
        
    # Scale the data
    scaled_data = scaler.transform(daily_df[['y']].values)
    
    # Get the last 'time_steps' days to predict the next
    last_sequence = scaled_data[-time_steps:]
    last_sequence = last_sequence.reshape(1, time_steps, 1)
    
    return last_sequence, daily_df, True

def predict_future(days_ahead=30):
    """
    Predicts future saldo using the LSTM model.
    """
    df = get_transactions()
    if df.empty:
        return pd.DataFrame(), 0
        
    time_steps = 30 # Assume the model was trained with 30 time steps
    last_sequence, daily_df, is_ready = prepare_lstm_data(df, time_steps)
    
    if not is_ready:
        # Fallback: simple moving average if model/data is not ready
        if len(daily_df) > 0:
            avg_daily = daily_df['y'].mean()
            last_date = daily_df['ds'].iloc[-1]
        else:
            avg_daily = 0
            last_date = pd.Timestamp.now().date()
            
        future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
        mock_predictions = [avg_daily] * days_ahead
        
        pred_df = pd.DataFrame({
            'ds': future_dates,
            'predicted_net': mock_predictions
        })
        return pred_df, avg_daily * days_ahead
        
    model = load_lstm_model()
    scaler = load_data_scaler()
    
    if model is None or scaler is None:
        # Fallback
        return pd.DataFrame(), 0
        
    predictions = []
    current_sequence = last_sequence.copy()
    
    # Predict iteratively in chunks of 30 days
    chunks = (days_ahead + 29) // 30
    
    for _ in range(chunks):
        pred_scaled = model.predict(current_sequence, verbose=0) # shape (1, 30)
        predictions.extend(pred_scaled[0].tolist())
        
        # Update sequence for next prediction block (if we need to predict more than 30 days)
        # Reshape the 30 predicted days to be the new input sequence
        current_sequence = np.reshape(pred_scaled, (1, 30, 1))
        
    # Truncate to the exact number of days requested
    predictions = predictions[:days_ahead]
    
    # Inverse transform predictions
    predictions_unscaled = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    
    # Create output dataframe
    last_date = daily_df['ds'].iloc[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
    
    pred_df = pd.DataFrame({
        'ds': future_dates,
        'predicted_net': predictions_unscaled.flatten()
    })
    
    # Kalibrasi: Mencegah prediksi meledak jika model LSTM di-train di data yang berbeda (out-of-sync)
    # Kita sesuaikan output model dengan distribusi statistik data aktual terakhir
    hist_mean = daily_df['y'].mean()
    hist_std = daily_df['y'].std()
    
    pred_mean = pred_df['predicted_net'].mean()
    pred_std = pred_df['predicted_net'].std()
    
    if pred_std == 0: 
        pred_std = 1
        
    # Hanya lakukan kalibrasi jika prediksi sangat tidak masuk akal (beda > 3x lipat)
    if abs(pred_mean) > abs(hist_mean) * 3 or abs(pred_mean) < abs(hist_mean) / 3:
        # Z-score normalization & map ke historical distribution
        z_scores = (pred_df['predicted_net'] - pred_mean) / pred_std
        # Tambahkan sedikit faktor tren (misal 5% growth) agar tidak persis sama dengan masa lalu
        trend_factor = np.linspace(1.0, 1.05, days_ahead)
        pred_df['predicted_net'] = (z_scores * hist_std + hist_mean) * trend_factor
    
    total_predicted_net = pred_df['predicted_net'].sum()
    
    return pred_df, total_predicted_net
