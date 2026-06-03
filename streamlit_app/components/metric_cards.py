import streamlit as st
from utils.helpers import format_currency

def render_metric_card(title, value, badge_text=None, badge_color=None):
    """
    Renders a custom styled metric card.
    """
    badge_html = ""
    if badge_text and badge_color:
        badge_html = f'<div class="health-badge {badge_color}">{badge_text}</div>'
        
    if isinstance(value, str):
        formatted_value = value
    else:
        formatted_value = format_currency(value)
        
    html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{formatted_value}</div>
        {badge_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
