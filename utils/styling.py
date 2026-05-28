NAVY = "#1B365D"
ORANGE = "#F37021"
LIGHT_PANEL = "#F5F7FA"
NAVY_SEQ = ["#1B365D", "#3A5A8C", "#6B89B5", "#9DB2D0", "#CED9E8"]

CUSTOM_CSS = """
<style>
    html, body, [class*="css"]  {
        font-family: Calibri, "Segoe UI", sans-serif !important;
    }
    .kpi-tile {
        background-color: #F5F7FA;
        border-left: 4px solid #F37021;
        padding: 16px 20px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .kpi-label {
        color: #1B365D;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .kpi-value {
        color: #1B365D;
        font-size: 32px;
        font-weight: 700;
        line-height: 1;
    }
    footer {visibility: hidden;}
    h1, h2, h3 {color: #1B365D;}
</style>
"""


def inject_css():
    """Call at the top of each page after st.set_page_config()."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def kpi_tile(label: str, value: str) -> str:
    """Return HTML for a single KPI tile."""
    return f'<div class="kpi-tile"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'
