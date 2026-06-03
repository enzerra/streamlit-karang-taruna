import streamlit as st
import pandas as pd
from services.supabase_service import fetch_transactions
from services.prediction_service import predict_future
from services.analytics_service import calculate_financial_metrics
from components.charts import render_prediction_chart
from utils.helpers import format_currency

def render():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Proyeksi Finansial Terpandu</div>
            <div class="hero-subtitle">Melihat ke Masa Depan dengan AI Karang Taruna</div>
        </div>
    """, unsafe_allow_html=True)
    
    df = fetch_transactions()
    metrics = calculate_financial_metrics(df)
    current_saldo = metrics.get('saldo', 0)
    
    st.markdown("### Ringkasan Proyeksi")
    st.markdown("Di halaman ini, sistem AI akan memprediksi tren keuangan Karang Taruna untuk 30 hari ke depan berdasarkan pola sejarah transaksi Anda.")
    st.markdown("---")
    
    with st.spinner("Menganalisis pola transaksi & menghitung prediksi..."):
        pred_df_30, total_pred_net = predict_future(days_ahead=30)
        is_ready = not pred_df_30.empty
        
    if not is_ready:
        st.warning("Data belum cukup untuk melakukan prediksi. Harap masukkan lebih banyak data transaksi.")
        return
        
    # Kalkulasi Saldo Prediksi
    # Proyeksi saldo akhir = saldo saat ini + total prediksi akumulasi net
    projected_saldo = current_saldo + total_pred_net
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Saldo Saat Ini**")
        st.subheader(format_currency(current_saldo))
    with col2:
        st.markdown("**Proyeksi Saldo (30 Hari)**")
        st.subheader(format_currency(projected_saldo))
    with col3:
        selisih = projected_saldo - current_saldo
        st.markdown("**Perkiraan Perubahan**")
        if selisih >= 0:
            st.subheader(f"📈 Naik {format_currency(selisih)}")
        else:
            st.subheader(f"📉 Turun {format_currency(selisih)}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Kesimpulan AI
    st.markdown("### 🤖 Kesimpulan AI")
    if projected_saldo < 0:
        st.error(f"**Peringatan Kritis:** Kas diprediksi akan mengalami **defisit** ({format_currency(projected_saldo)}) pada akhir bulan depan. Segera lakukan penghematan drastis atau cari pendanaan baru.")
    elif projected_saldo < current_saldo:
        st.warning(f"**Hati-hati:** Saldo diprediksi akan **menyusut**. Pastikan pengeluaran bulan depan tidak melebihi rencana.")
    else:
        st.success(f"**Aman:** Tren keuangan positif. Saldo diprediksi akan **tumbuh** dan mencukupi untuk kegiatan Karang Taruna berikutnya.")

    st.markdown("---")
    render_prediction_chart(df, pred_df_30, "Grafik Perjalanan Saldo: Historis vs Prediksi")
