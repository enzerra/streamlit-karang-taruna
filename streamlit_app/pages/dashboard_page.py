import streamlit as st
from services.supabase_service import fetch_transactions
from services.analytics_service import calculate_financial_metrics, calculate_health_score
from components.metric_cards import render_metric_card
from components.charts import render_trend_chart
from components.insights import render_insights

def render():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Karang Taruna Analytics</div>
            <div class="hero-subtitle">AI Financial Dashboard</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Fetch Data
    df = fetch_transactions()
    metrics = calculate_financial_metrics(df)
    health = calculate_health_score(df)
    
    # Metric Cards Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Saldo Saat Ini", metrics['saldo'])
    with col2:
        render_metric_card("Pemasukan", metrics['pemasukan'])
    with col3:
        render_metric_card("Pengeluaran", metrics['pengeluaran'])
    with col4:
        render_metric_card("Health Score", f"{health['score']}/100", health['status'], health['color'])
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Chart & Insights Row
    col_chart, col_insight = st.columns([2, 1])
    
    with col_chart:
        render_trend_chart(df, "Trend Saldo Keseluruhan")
        
    with col_insight:
        render_insights(metrics, df)
