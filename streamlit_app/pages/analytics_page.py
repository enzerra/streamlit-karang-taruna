import streamlit as st
import plotly.express as px
import pandas as pd
from services.supabase_service import fetch_transactions

def render():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Analisis Keuangan Terperinci</div>
            <div class="hero-subtitle">Melihat Lebih Dalam Arus Kas Karang Taruna</div>
        </div>
    """, unsafe_allow_html=True)
    
    df = fetch_transactions()
    if df.empty:
        st.info("Tidak ada data untuk dianalisis.")
        return
        
    st.markdown("### 🏆 Top 3 Pengeluaran Terbesar")
    st.markdown("Transaksi keluar yang paling menguras kas organisasi:")
    
    pengeluaran_df = df[df['type'].str.lower() == 'pengeluaran']
    
    if not pengeluaran_df.empty:
        # Karena pengeluaran bernilai negatif, pengeluaran terbesar adalah nilai terkecil (paling negatif)
        top_expenses = pengeluaran_df.sort_values(by='amount', ascending=True).head(3)
        
        # Display as cards or table
        cols = st.columns(3)
        for i, (_, row) in enumerate(top_expenses.iterrows()):
            with cols[i]:
                cat = row.get('category', 'Lainnya')
                desc = row.get('desc', '-')
                # Gunakan abs() agar tanda minus tidak muncul di UI
                amt = f"Rp {abs(float(row['amount'])):,.0f}".replace(",", ".")
                date_str = row['date'].strftime('%d %b %Y') if pd.notnull(row['date']) else '-'
                
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid #ef4444; padding: 16px;">
                    <h4 style="margin:0; color:#ef4444;">#{i+1} {cat}</h4>
                    <p style="font-size: 0.9rem; color:#64748b; margin-top:4px;">{desc}</p>
                    <h3 style="margin:0;">{amt}</h3>
                    <p style="font-size: 0.8rem; color:#94a3b8; margin-top:4px;">{date_str}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Belum ada data pengeluaran.")
        
    st.markdown("---")
    st.markdown("### Komposisi Kategori (Pemasukan vs Pengeluaran)")
    
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        st.markdown("**Pengeluaran Berdasarkan Kategori**")
        if not pengeluaran_df.empty and 'category' in pengeluaran_df.columns:
            cat_df = pengeluaran_df.groupby('category')['amount'].sum().reset_index()
            cat_df['amount'] = cat_df['amount'].abs() # Ubah ke positif untuk pie chart
            fig_pie = px.pie(cat_df, values='amount', names='category', hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Reds_r)
            fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Tidak ada data kategori pengeluaran.")
            
    with col_pie2:
        st.markdown("**Pemasukan Berdasarkan Kategori**")
        pemasukan_df = df[df['type'].str.lower() == 'pemasukan']
        if not pemasukan_df.empty and 'category' in pemasukan_df.columns:
            cat_df_in = pemasukan_df.groupby('category')['amount'].sum().reset_index()
            fig_pie_in = px.pie(cat_df_in, values='amount', names='category', hole=0.4,
                                color_discrete_sequence=px.colors.sequential.Greens_r)
            fig_pie_in.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
            st.plotly_chart(fig_pie_in, use_container_width=True)
        else:
            st.info("Tidak ada data kategori pemasukan.")

    st.markdown("---")
    st.markdown("### Riwayat Transaksi Lengkap")
    # Clean up dataframe for display
    display_df = df.copy()
    if 'amount' in display_df.columns:
        display_df['amount_rp'] = display_df['amount'].apply(lambda x: f"Rp {float(x):,.0f}".replace(",", "."))
    if 'date' in display_df.columns:
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    
    # Pilih kolom yang benar-benar ada di dataframe
    desired_cols = ['date', 'type', 'category', 'desc', 'description', 'amount_rp']
    available_cols = [col for col in desired_cols if col in display_df.columns]
    
    st.dataframe(display_df[available_cols].sort_values(by='date', ascending=False), use_container_width=True)
