import streamlit as st
from services.supabase_service import fetch_transactions
from services.analytics_service import calculate_financial_metrics
from components.insights import render_insights

def render():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Executive Summary</div>
            <div class="hero-subtitle">Ringkasan Cerdas untuk Pengambilan Keputusan Karang Taruna</div>
        </div>
    """, unsafe_allow_html=True)
    
    df = fetch_transactions()
    metrics = calculate_financial_metrics(df)
    
    render_insights(metrics, df)
