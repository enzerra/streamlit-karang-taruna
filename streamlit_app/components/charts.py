import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from utils.preprocessing import aggregate_daily_transactions

def render_trend_chart(df: pd.DataFrame, title="Trend Transaksi"):
    """
    Renders a line chart for transactions trend using Plotly.
    """
    if df.empty:
        st.info("Tidak ada data untuk ditampilkan.")
        return
        
    daily_df = aggregate_daily_transactions(df)
    if daily_df.empty:
        st.info("Tidak ada data harian untuk ditampilkan.")
        return
        
    fig = px.line(
        daily_df, 
        x="ds", 
        y="y", 
        title=title,
        labels={"ds": "Tanggal", "y": "Net Saldo (Rp)"},
        template="plotly_white"
    )
    
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
    )
    
    # Modern line style
    fig.update_traces(line=dict(width=3, color="#3b82f6"))
    
    st.plotly_chart(fig, use_container_width=True)

def render_prediction_chart(historical_df: pd.DataFrame, prediction_df: pd.DataFrame, title="Prediksi Saldo"):
    """
    Renders historical and predicted data on the same chart.
    """
    fig = go.Figure()
    
    # Historical Data
    if not historical_df.empty:
        daily_df = aggregate_daily_transactions(historical_df)
        if not daily_df.empty:
            fig.add_trace(go.Scatter(
                x=daily_df['ds'], 
                y=daily_df['y'],
                mode='lines',
                name='Historis',
                line=dict(color='#64748b', width=2)
            ))
            
    # Prediction Data
    if not prediction_df.empty:
        fig.add_trace(go.Scatter(
            x=prediction_df['ds'], 
            y=prediction_df['predicted_net'],
            mode='lines',
            name='Prediksi',
            line=dict(color='#8b5cf6', width=3, dash='dash')
        ))
        
    # Tambahkan garis penanda "Hari Ini"
    if not daily_df.empty:
        last_date = daily_df['ds'].iloc[-1]
        fig.add_vline(x=last_date, line_width=2, line_dash="dash", line_color="red")
        fig.add_annotation(x=last_date, y=1, yref="paper", text="Hari Ini", showarrow=False, xanchor="left", font=dict(color="red"))
        
    fig.update_layout(
        title=title,
        template="plotly_white",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
    )
    
    st.plotly_chart(fig, use_container_width=True)
