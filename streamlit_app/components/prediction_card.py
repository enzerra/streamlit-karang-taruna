import streamlit as st
from utils.helpers import format_currency

def render_prediction_card(days_ahead, predicted_total_change, is_ready=True):
    """
    Renders a specialized card for displaying prediction results.
    """
    if not is_ready:
        html = f"""
        <div class="metric-card">
            <div class="metric-title">Prediksi {days_ahead} Hari</div>
            <div class="metric-value" style="font-size: 1.25rem; color: #94a3b8;">
                Model belum siap / Data tidak cukup
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        return
        
    color_class = "green" if predicted_total_change >= 0 else "red"
    trend_icon = "↗️" if predicted_total_change >= 0 else "↘️"
    trend_text = "Naik" if predicted_total_change >= 0 else "Turun"
    
    formatted_val = format_currency(abs(predicted_total_change))
    
    html = f"""
        <div class="metric-card" style="border-left: 4px solid {'#10b981' if predicted_total_change >= 0 else '#ef4444'};">
            <div class="metric-title">Prediksi Perubahan ({days_ahead} Hari)</div>
            <div class="metric-value">
                {trend_icon} {formatted_val}
            </div>
            <div class="health-badge {color_class}">
                Diprediksi {trend_text}
            </div>
        </div>
    """
    st.markdown(html, unsafe_allow_html=True)
