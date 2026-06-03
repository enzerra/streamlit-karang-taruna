import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from scipy.stats import ttest_ind
from datetime import datetime
import warnings
import joblib

# --- Import Supabase & Keras ---
from supabase import create_client, Client
from tensorflow.keras.models import load_model

warnings.filterwarnings('ignore')

# ============================================================
# KONFIGURASI HALAMAN & TEMA
# ============================================================
st.set_page_config(
    page_title="SIKARTA AI Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hapus margin bawaan Streamlit yang berlebihan
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.block-container { padding-top: 2rem !important; max-width: 1300px !important; }
.stTabs [data-baseweb="tab-list"] { gap: 32px; border-bottom: 1px solid #E5E7EB; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border: none !important; color: #6B7280 !important; font-weight: 500 !important; padding: 12px 0 !important; }
.stTabs [aria-selected="true"] { color: #1B3A6B !important; border-bottom: 2px solid #1B3A6B !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# KONSTANTA & FORMATTER HELPERS
# ============================================================
MONTH_ID = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}
MONTH_SHORT = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}

def rupiah(n, singkat=False):
    try:
        n = float(n)
        if np.isnan(n): n = 0.0
    except: n = 0.0
    n = int(n)
    negatif = n < 0
    absn = abs(n)
    
    if singkat:
        if absn >= 1_000_000_000: teks = f"Rp {absn/1_000_000_000:.1f} M"
        elif absn >= 1_000_000:   teks = f"Rp {absn/1_000_000:.1f} jt"
        elif absn >= 1_000:       teks = f"Rp {absn/1_000:.0f} rb"
        else:                      teks = f"Rp {absn:,}".replace(",", ".")
    else:
        teks = f"Rp {absn:,}".replace(",", ".")
        
    return f"-{teks}" if negatif else teks

# ============================================================
# DATA & ML
# ============================================================
@st.cache_resource
def init_supabase() -> Client:
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        st.error("Gagal terhubung ke database Supabase.")
        st.stop()

@st.cache_resource
def load_ml_assets():
    try:
        return load_model("model_lstm.keras"), joblib.load("scaler.pkl")
    except:
        return None, None

@st.cache_data(ttl=60)
def fetch_data_from_supabase(_supabase: Client) -> pd.DataFrame:
    try:
        response = _supabase.table("transactions").select("*").order("date").execute()
        df = pd.DataFrame(response.data)
        if df.empty: return pd.DataFrame()
        
        df["Tanggal"] = pd.to_datetime(df["date"])
        df["Pemasukan"] = np.where(df["type"] == "Pemasukan", df["amount"], 0)
        df["Pengeluaran"] = np.where(df["type"] == "Pengeluaran", df["amount"], 0)
        df["Kategori"] = df["category"] if "category" in df.columns else "Umum"
        df['Tahun'] = df['Tanggal'].dt.year
        df['Bulan'] = df['Tanggal'].dt.month
        df['Hari']  = df['Tanggal'].dt.day
        df['BulanNama'] = df['Bulan'].map(MONTH_ID)
        df['BulanPendek'] = df['Bulan'].map(MONTH_SHORT)
        df["Saldo"] = df["Pemasukan"].cumsum() - df["Pengeluaran"].cumsum()
        return df.sort_values('Tanggal').reset_index(drop=True)
    except:
        return pd.DataFrame()

def agregasi_bulanan(df: pd.DataFrame, tahun: int) -> pd.DataFrame:
    d = df[df['Tahun'] == tahun]
    if d.empty: return pd.DataFrame()
    m = (d.groupby(['Bulan','BulanNama','BulanPendek'])
         .agg(Pemasukan=('Pemasukan','sum'), Pengeluaran=('Pengeluaran','sum'),
              SaldoAkhir=('Saldo','last'))
         .reset_index().sort_values('Bulan'))
    m['Surplus'] = m['Pemasukan'] - m['Pengeluaran']
    m['RasioBeban'] = np.where(m['Pemasukan'] > 0, m['Pengeluaran'] / m['Pemasukan'] * 100, 100.0)
    m['Status'] = m['Surplus'].apply(lambda x: 'Surplus' if x >= 0 else 'Defisit')
    return m

# ============================================================
# COMPONENT RENDERERS
# ============================================================
def ui_card(title, value, subtitle, val_color="#111827", bg_color="#FFFFFF", top_border="transparent"):
    return f"""
    <div style="background-color: {bg_color}; padding: 24px; border-radius: 12px; border: 1px solid #E5E7EB; border-top: 4px solid {top_border}; box-shadow: 0 2px 10px rgba(0,0,0,0.02); height: 100%;">
        <p style="color: #6B7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin: 0 0 8px 0; letter-spacing: 0.05em;">{title}</p>
        <h3 style="color: {val_color}; font-size: 1.75rem; font-weight: 700; margin: 0 0 4px 0; letter-spacing: -0.02em;">{value}</h3>
        <p style="color: #9CA3AF; font-size: 0.8rem; margin: 0;">{subtitle}</p>
    </div>
    """

def ui_alert(title, text, type="info"):
    colors = {
        "info": {"bg": "#EFF6FF", "border": "#3B82F6", "text": "#1D4ED8"},
        "success": {"bg": "#ECFDF5", "border": "#10B981", "text": "#047857"},
        "warning": {"bg": "#FFFBEB", "border": "#F59E0B", "text": "#B45309"},
        "danger": {"bg": "#FEF2F2", "border": "#EF4444", "text": "#B91C1C"}
    }
    c = colors.get(type, colors["info"])
    return f"""
    <div style="background-color: {c['bg']}; border-left: 4px solid {c['border']}; padding: 16px 20px; border-radius: 6px; margin-bottom: 16px;">
        <h4 style="color: {c['text']}; margin: 0 0 4px 0; font-size: 0.95rem; font-weight: 600;">{title}</h4>
        <p style="color: {c['text']}; margin: 0; font-size: 0.85rem; opacity: 0.9;">{text}</p>
    </div>
    """

def ui_section(title):
    st.markdown(f"""
    <h2 style="font-size: 1.15rem; font-weight: 600; color: #111827; margin: 32px 0 20px 0; padding-bottom: 8px; border-bottom: 1px solid #E5E7EB;">{title}</h2>
    """, unsafe_allow_html=True)

# ============================================================
# MAIN APPLICATION
# ============================================================
def main():
    supabase_client = init_supabase()
    df_transactions = fetch_data_from_supabase(supabase_client)
    
    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 20px;">
            <h2 style="font-size: 1.25rem; font-weight: 700; color: #111827; margin: 0;">SIKARTA AI</h2>
            <p style="font-size: 0.85rem; color: #6B7280; margin: 2px 0 0 0;">Intelligence Dashboard v4.1</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("Terkoneksi ke Supabase")
        if st.button("🔄 Sinkronisasi Ulang", use_container_width=True):
            fetch_data_from_supabase.clear()
            st.rerun()
            
        if df_transactions.empty:
            st.warning("Database Transaksi Kosong.")
            return
            
        st.markdown("<br>", unsafe_allow_html=True)
        list_tahun = sorted(df_transactions['Tahun'].unique(), reverse=True)
        tahun_pilihan = st.selectbox("Tahun Buku", options=list_tahun)
        list_bulan = ["Semua Bulan"] + [MONTH_ID[b] for b in sorted(df_transactions[df_transactions['Tahun'] == tahun_pilihan]['Bulan'].unique())]
        bulan_pilihan = st.selectbox("Periode", options=list_bulan)

    # --------------------------------------------------------
    # HEADER UTAMA
    # --------------------------------------------------------
    st.markdown("""
    <div style="margin-bottom: 30px;">
        <h1 style="font-size: 1.85rem; font-weight: 700; color: #111827; margin: 0; letter-spacing: -0.02em;">Dashboard Analitik Karang Taruna</h1>
        <p style="font-size: 1rem; color: #6B7280; margin: 6px 0 0 0;">Konsolidasi operasional terintegrasi dengan pemodelan forecasting AI.</p>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # DATA PREP
    # --------------------------------------------------------
    m_buku = agregasi_bulanan(df_transactions, tahun_pilihan)
    if m_buku.empty:
        st.error("Gagal melakukan kalkulasi ringkasan data tahunan.")
        return
        
    m_filtered = m_buku.copy()
    if bulan_pilihan != "Semua Bulan":
        num_bln = {v: k for k, v in MONTH_ID.items()}.get(bulan_pilihan)
        m_filtered = m_buku[m_buku['Bulan'] == num_bln]

    # --------------------------------------------------------
    # TABS LAYOUT
    # --------------------------------------------------------
    t_ringkasan, t_grafik, t_prediksi, t_audit = st.tabs([
        "Ringkasan Eksekutif", 
        "Visualisasi Data", 
        "Inteligensi AI", 
        "Jurnal Transaksi"
    ])
    
    # TAB 1: RINGKASAN EKSEKUTIF
    with t_ringkasan:
        sal = m_filtered['SaldoAkhir'].iloc[-1]
        ti = m_filtered['Pemasukan'].sum()
        to = m_filtered['Pengeluaran'].sum()
        sur = ti - to
        pct = (sur / ti * 100) if ti > 0 else 0.0
        
        ui_section(f"Indikator Kinerja Utama ({bulan_pilihan} - {tahun_pilihan})")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(ui_card("Saldo Kas", rupiah(sal, True), "Dana operasional aktif", "#1B3A6B", top_border="#1B3A6B"), unsafe_allow_html=True)
        c2.markdown(ui_card("Total Pemasukan", rupiah(ti, True), f"Dari {len(m_filtered)} bulan berjalan", "#059669", top_border="#059669"), unsafe_allow_html=True)
        c3.markdown(ui_card("Total Pengeluaran", rupiah(to, True), "Alokasi program/rutin", "#DC2626", top_border="#DC2626"), unsafe_allow_html=True)
        c4.markdown(ui_card("Net Margin", rupiah(sur, True), f"Rasio Surplus: {pct:.1f}%", "#2563EB" if sur >= 0 else "#DC2626", top_border="#F39C12"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if sur < 0:
            st.markdown(ui_alert("Defisit Terdeteksi", "Pengeluaran melampaui pemasukan pada periode ini. Disarankan melakukan penyesuaian alokasi dana.", "danger"), unsafe_allow_html=True)
        elif pct > 20:
            st.markdown(ui_alert("Kinerja Keuangan Sehat", "Organisasi berhasil mempertahankan surplus yang sangat baik, ideal untuk dialokasikan pada program baru.", "success"), unsafe_allow_html=True)

    # TAB 2: VISUALISASI
    with t_grafik:
        ui_section(f"Analisis Arus Kas Tahun {tahun_pilihan}")
        cg1, cg2 = st.columns([2, 1])
        
        with cg1:
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=m_filtered['BulanPendek'], y=m_filtered['Pemasukan'], name='Masuk', marker_color='#1B3A6B'))
            fig1.add_trace(go.Bar(x=m_filtered['BulanPendek'], y=m_filtered['Pengeluaran'], name='Keluar', marker_color='#F39C12'))
            fig1.update_layout(title="Perbandingan Masuk vs Keluar", barmode='group', margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#6B7280"))
            st.plotly_chart(fig1, use_container_width=True)
            
        with cg2:
            fig2 = go.Figure(go.Pie(labels=['Keluar', 'Sisa/Surplus'], values=[to, max(0, sur)], hole=0.7, marker=dict(colors=['#F39C12', '#1B3A6B'])))
            fig2.update_layout(title="Rasio Distribusi", margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#6B7280"), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # TAB 3: AI
    with t_prediksi:
        ui_section("Inteligensi Buatan (LSTM Forecasting)")
        st.markdown(ui_alert("Menunggu Konfigurasi Streamlit ML", "Sistem model LSTM sedang dikonfigurasi ulang secara independen oleh Tim Data Science untuk kompatibilitas data harian Supabase.", "info"), unsafe_allow_html=True)
        st.write("Silakan kembali lagi nanti setelah modul prediksi selesai dikalibrasi.")

    # TAB 4: AUDIT
    with t_audit:
        ui_section(f"Buku Besar Bulanan — {tahun_pilihan}")
        tampil = m_buku[['BulanNama','Pemasukan','Pengeluaran','Surplus','SaldoAkhir']].copy()
        tampil.columns = ['Periode','Uang Masuk','Uang Keluar','Margin','Saldo Akhir']
        for col in ['Uang Masuk','Uang Keluar','Margin','Saldo Akhir']: 
            tampil[col] = tampil[col].apply(rupiah)
        
        st.dataframe(tampil, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()