import streamlit as st

def render_sidebar():
    """Renders the sidebar navigation and returns the selected page."""
    with st.sidebar:
        # Display logo (placeholder for actual logo)
        # st.image("assets/logo.png", width=150)
        st.markdown("### Karang Taruna")
        st.markdown("---")
        
        selected = st.radio(
            "Navigasi",
            ["🏠 Dashboard", "📈 Prediksi Saldo", "📊 Analisis Keuangan", "🤖 AI Insight"],
            label_visibility="hidden"
        )
        
        st.markdown("---")
        st.caption("© 2026 Digitalisasi Karang Taruna")
        
        # Strip emojis for cleaner page names returned
        if "Dashboard" in selected:
            return "Dashboard"
        elif "Prediksi" in selected:
            return "Prediksi"
        elif "Analisis" in selected:
            return "Analisis"
        elif "AI Insight" in selected:
            return "Insights"
            
        return "Dashboard"
