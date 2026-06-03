import streamlit as st
import pandas as pd
from utils.helpers import format_currency

def calculate_runway(df: pd.DataFrame, current_saldo: float) -> str:
    """Calculates how many months the current balance will last based on average monthly expenses."""
    pengeluaran_df = df[df['type'].str.lower() == 'pengeluaran'].copy()
    if pengeluaran_df.empty or current_saldo <= 0:
        return "N/A"
        
    pengeluaran_df['month_year'] = pengeluaran_df['date'].dt.to_period('M')
    monthly_expenses = pengeluaran_df.groupby('month_year')['amount'].sum()
    
    avg_monthly_expense = abs(monthly_expenses.mean())
    
    if avg_monthly_expense == 0:
        return "Aman (Tidak ada pengeluaran rutin)"
        
    months_left = current_saldo / avg_monthly_expense
    return f"{months_left:.1f} Bulan"

def generate_executive_summary(metrics: dict, df: pd.DataFrame):
    """
    Generates a structured executive summary and early warnings.
    """
    saldo = metrics.get('saldo', 0)
    pemasukan = metrics.get('pemasukan', 0)
    pengeluaran = metrics.get('pengeluaran', 0)
    
    runway = calculate_runway(df, saldo)
    
    insights = {
        "runway": runway,
        "warnings": [],
        "opportunities": [],
        "status": ""
    }
    
    # Executive Status
    if saldo < 0:
        insights["status"] = "Kritis (Kas Defisit)"
    elif pengeluaran > pemasukan:
        insights["status"] = "Perhatian (Pengeluaran > Pemasukan)"
    else:
        insights["status"] = "Sehat (Kas Bertumbuh)"
        
    # Warnings
    if pengeluaran > pemasukan:
        insights["warnings"].append("Total pengeluaran Anda saat ini melebihi total pemasukan. Jika tren ini berlanjut, kas akan tergerus.")
    if saldo < 1000000 and saldo > 0:
        insights["warnings"].append("Saldo kas menipis (di bawah Rp 1.000.000). Harap tahan pengeluaran non-esensial.")
        
    # Opportunities
    if not df.empty and 'category' in df.columns:
        pengeluaran_df = df[df['type'].str.lower() == 'pengeluaran']
        if not pengeluaran_df.empty:
            cat_sum = pengeluaran_df.groupby('category')['amount'].sum()
            top_category = cat_sum.idxmax()
            top_percent = (cat_sum.max() / pengeluaran) * 100
            
            insights["opportunities"].append(f"Kategori **{top_category}** menyedot **{top_percent:.0f}%** dari total pengeluaran. Mengevaluasi anggaran kategori ini dapat memberikan penghematan signifikan.")
            
    if saldo > (pengeluaran * 2) and pengeluaran > 0:
         insights["opportunities"].append("Saldo kas saat ini lebih dari dua kali lipat total pengeluaran. Anda memiliki ruang aman untuk mendanai program inovasi Karang Taruna.")
         
    return insights

def render_insights(metrics: dict, df: pd.DataFrame):
    """
    Renders the insights as Streamlit elements.
    """
    data = generate_executive_summary(metrics, df)
    
    st.markdown("### 🤖 Ringkasan Eksekutif (AI)")
    st.markdown(f"**Status Saat Ini:** `{data['status']}`")
    st.markdown(f"**Ketahanan Kas (Runway):** `{data['runway']}` *(Seberapa lama kas bertahan tanpa pemasukan baru)*")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚨 Peringatan Dini")
        if data["warnings"]:
            for w in data["warnings"]:
                st.warning(w)
        else:
            st.success("Tidak ada peringatan dini. Semua indikator aman.")
            
    with col2:
        st.markdown("#### 💡 Peluang Penghematan & Aksi")
        if data["opportunities"]:
            for o in data["opportunities"]:
                st.info(o)
        else:
            st.info("Pertahankan tren keuangan Anda saat ini.")
