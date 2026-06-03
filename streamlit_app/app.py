import streamlit as st
import os
from config.settings import settings

# Must be the first Streamlit command
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    css_path = os.path.join("assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Import UI components and pages
from pages import dashboard_page, prediction_page, analytics_page, insights_page

def main():
    with st.sidebar:
        st.markdown("### Karang Taruna")
        st.caption("AI Financial Dashboard")
        st.markdown("---")

    dashboard = st.Page(dashboard_page.render, title="Dashboard", icon=":material/dashboard:", url_path="dashboard")
    prediction = st.Page(prediction_page.render, title="Prediksi Saldo", icon=":material/trending_up:", url_path="prediksi")
    analytics = st.Page(analytics_page.render, title="Analisis Keuangan", icon=":material/analytics:", url_path="analisis")
    insights = st.Page(insights_page.render, title="AI Insight", icon=":material/lightbulb:", url_path="insight")

    pg = st.navigation([dashboard, prediction, analytics, insights])
    
    with st.sidebar:
        st.markdown("---")
        st.caption("© 2026 Digitalisasi Karang Taruna")
        
    pg.run()

if __name__ == "__main__":
    main()
