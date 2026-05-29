import streamlit as st
from utils.styling import inject_css

st.set_page_config(
    page_title="Payer PA Policy Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

pg = st.navigation([
    st.Page("pages/1_Landscape.py",       title="Landscape Overview",  icon="📊"),
    st.Page("pages/2_Policy_Drilldown.py", title="Policy Drilldown",    icon="🔍"),
    st.Page("pages/3_Brand_Comparison.py", title="Brand Comparison",    icon="⚖️"),
])
pg.run()
