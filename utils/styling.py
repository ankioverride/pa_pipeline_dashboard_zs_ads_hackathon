NAVY = "#1B365D"
ORANGE = "#F37021"
LIGHT_PANEL = "#F5F7FA"
NAVY_SEQ = ["#1B365D", "#3A5A8C", "#6B89B5", "#9DB2D0", "#CED9E8"]

GREEN_GOOD = "#2E7D32"
RED_BAD = "#C62828"
AMBER = "#E65100"
SCORE_COLORS = {50: "#C62828", 75: "#E65100", 100: "#2E7D32"}
SCORE_BG = {50: "#FFEBEE", 75: "#FFF3E0", 100: "#E8F5E9"}

CUSTOM_CSS = """
<style>
html, body, [class*="css"] {
    font-family: Calibri, "Segoe UI", sans-serif !important;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1B365D 0%, #2C5282 60%, #3A5A8C 100%);
    border-radius: 14px;
    padding: 32px 40px;
    margin-bottom: 24px;
    color: white;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: "";
    position: absolute; top: -50px; right: -50px;
    width: 220px; height: 220px;
    background: rgba(243,112,33,0.15);
    border-radius: 50%;
}
.hero-banner::after {
    content: "";
    position: absolute; bottom: -30px; right: 120px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.hero-title { font-size: 26px; font-weight: 700; margin: 0 0 4px 0; letter-spacing: -0.3px; }
.hero-subtitle { font-size: 13px; opacity: 0.75; margin: 0 0 24px 0; }
.hero-stats { display: flex; gap: 36px; flex-wrap: wrap; }
.hero-stat { text-align: center; min-width: 80px; }
.hero-stat-num { font-size: 26px; font-weight: 700; color: #F37021; line-height: 1; }
.hero-stat-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7; margin-top: 4px; }
.hero-divider { width: 1px; background: rgba(255,255,255,0.2); align-self: stretch; }

/* ── Stat Cards ── */
.stat-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 18px 16px 14px;
    box-shadow: 0 2px 10px rgba(27,54,93,0.09);
    border-top: 3px solid #F37021;
    margin-bottom: 8px;
    min-height: 112px;
    position: relative;
    overflow: hidden;
}
.stat-card::after {
    content: "";
    position: absolute; bottom: -20px; right: -10px;
    width: 80px; height: 80px;
    background: rgba(27,54,93,0.03);
    border-radius: 50%;
}
.stat-icon { font-size: 20px; margin-bottom: 8px; display: block; }
.stat-label {
    color: #8A94A6; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.9px; margin-bottom: 4px;
}
.stat-value {
    color: #1B365D; font-size: 26px; font-weight: 700; line-height: 1.1;
}
.stat-delta {
    display: inline-block; font-size: 10px; font-weight: 600;
    padding: 2px 8px; border-radius: 12px; margin-top: 6px;
}
.delta-good { background: #E8F5E9; color: #2E7D32; }
.delta-neutral { background: #F3F4F6; color: #6B7280; }
.delta-bad { background: #FFEBEE; color: #C62828; }

/* ── Section Headers ── */
.section-header {
    display: flex; align-items: flex-start; gap: 10px;
    margin: 28px 0 14px 0; padding-bottom: 12px;
    border-bottom: 1px solid #E9ECF0;
}
.section-title-bar {
    width: 4px; min-height: 32px; background: #F37021;
    border-radius: 2px; flex-shrink: 0; margin-top: 2px;
}
.section-header-text {}
.section-header-title {
    color: #1B365D; font-size: 15px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.6px; margin: 0;
}
.section-header-subtitle { color: #9CA3AF; font-size: 12px; margin-top: 2px; }

/* ── Badge Pills ── */
.badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 700;
    letter-spacing: 0.3px; text-transform: uppercase; line-height: 1.6;
}
.badge-green  { background: #E8F5E9; color: #2E7D32; }
.badge-red    { background: #FFEBEE; color: #C62828; }
.badge-amber  { background: #FFF3E0; color: #E65100; }
.badge-gray   { background: #F3F4F6; color: #6B7280; }
.badge-navy   { background: #E8EEF6; color: #1B365D; }

/* ── Score Chips ── */
.score-chip { font-weight: 700; padding: 5px 14px; border-radius: 20px; font-size: 14px; display: inline-block; }
.score-chip-50  { background: #FFEBEE; color: #C62828; }
.score-chip-75  { background: #FFF3E0; color: #E65100; }
.score-chip-100 { background: #E8F5E9; color: #2E7D32; }

/* ── Policy Card (Drilldown) ── */
.policy-card {
    background: #fff; border-radius: 14px; overflow: hidden;
    box-shadow: 0 4px 20px rgba(27,54,93,0.12); margin-top: 20px;
}
.policy-card-header {
    background: linear-gradient(90deg, #1B365D 0%, #3A5A8C 100%);
    color: white; padding: 20px 26px;
    display: flex; justify-content: space-between; align-items: center;
}
.policy-card-header-title { font-size: 15px; font-weight: 700; }
.policy-card-header-sub { font-size: 12px; opacity: 0.72; margin-top: 3px; }
.policy-card-body { padding: 22px 26px; }
.field-group { margin-bottom: 16px; }
.field-label {
    color: #9CA3AF; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 4px;
}
.field-value { color: #1B365D; font-weight: 600; font-size: 14px; }
.long-text-box {
    background: #F8F9FB; border: 1px solid #E5E7EB;
    border-left: 3px solid #3A5A8C; border-radius: 8px;
    padding: 14px 16px; font-size: 13px; color: #374151;
    max-height: 160px; overflow-y: auto; line-height: 1.65;
    font-family: Calibri, "Segoe UI", sans-serif; white-space: pre-wrap;
    margin-bottom: 8px;
}

/* ── Scorecard bar ── */
.scorecard-bar-bg {
    background: #E5E7EB; border-radius: 6px; height: 10px; width: 100%;
}
.scorecard-bar-fill {
    background: linear-gradient(90deg, #1B365D, #3A5A8C);
    border-radius: 6px; height: 10px; transition: width 0.4s ease;
}

/* ── Restrictiveness Cards ── */
.restrict-card {
    background: #fff; border-radius: 10px; padding: 14px 18px;
    box-shadow: 0 2px 8px rgba(27,54,93,0.07);
    border-left: 4px solid transparent;
    margin-bottom: 10px; display: flex;
    justify-content: space-between; align-items: center;
}
.restrict-card-most  { border-left-color: #C62828; }
.restrict-card-least { border-left-color: #2E7D32; }
.restrict-card-name  { font-weight: 700; color: #1B365D; font-size: 13px; }
.restrict-card-brand { color: #6B7280; font-size: 11px; margin-top: 2px; }

/* ── Result Badge ── */
.result-badge {
    background: #1B365D; color: white; padding: 4px 14px;
    border-radius: 20px; font-size: 12px; font-weight: 600;
    display: inline-block; margin-bottom: 12px;
}

/* ── Search input rounding ── */
.stTextInput > div > div > input {
    border-radius: 24px !important;
    border: 2px solid #D1D9E6 !important;
    padding-left: 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1B365D !important;
    box-shadow: 0 0 0 2px rgba(27,54,93,0.15) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B365D 0%, #2C5282 100%) !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #CBD5E0 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* ── Table row striping ── */
.stDataFrame tbody tr:nth-child(even) { background-color: #F8FAFC !important; }
.stDataFrame tbody tr:hover { background-color: #EEF2F8 !important; }

/* ── Misc ── */
footer { visibility: hidden; }
h1, h2, h3 { color: #1B365D; }
.stPlotlyChart { border-radius: 10px; overflow: hidden; }
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def kpi_tile(label: str, value: str) -> str:
    return f'<div class="kpi-tile"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'


def access_score_badge(score) -> str:
    score = int(score)
    css = SCORE_COLORS.get(score, "#6B7280")
    bg = SCORE_BG.get(score, "#F3F4F6")
    return f'<span class="score-chip score-chip-{score}" style="background:{bg};color:{css}">{score}</span>'


def yes_no_badge(val: str, good_is_yes: bool = True) -> str:
    v = str(val).strip()
    if v == "Yes":
        cls = "badge-green" if good_is_yes else "badge-red"
    elif v == "No":
        cls = "badge-red" if good_is_yes else "badge-green"
    else:
        cls = "badge-gray"
    return f'<span class="badge {cls}">{v}</span>'


def section_header(title: str, subtitle: str = "") -> str:
    sub_html = f'<div class="section-header-subtitle">{subtitle}</div>' if subtitle else ""
    return f"""<div class="section-header">
  <div class="section-title-bar"></div>
  <div class="section-header-text">
    <div class="section-header-title">{title}</div>
    {sub_html}
  </div>
</div>"""


def stat_card(icon: str, label: str, value: str, delta: str = None, delta_type: str = "neutral") -> str:
    delta_html = ""
    if delta:
        delta_html = f'<div class="stat-delta delta-{delta_type}">{delta}</div>'
    return f"""<div class="stat-card">
  <span class="stat-icon">{icon}</span>
  <div class="stat-label">{label}</div>
  <div class="stat-value">{value}</div>
  {delta_html}
</div>"""


def hero_banner(title: str, subtitle: str, stats: list) -> str:
    stats_html = ""
    for i, s in enumerate(stats):
        if i > 0:
            stats_html += '<div class="hero-divider"></div>'
        stats_html += f"""<div class="hero-stat">
  <div class="hero-stat-num">{s["num"]}</div>
  <div class="hero-stat-label">{s["label"]}</div>
</div>"""
    return f"""<div class="hero-banner">
  <div class="hero-title">{title}</div>
  <div class="hero-subtitle">{subtitle}</div>
  <div class="hero-stats">{stats_html}</div>
</div>"""


def restrict_card(filename: str, brand: str, score: int, side: str) -> str:
    cls = "restrict-card-most" if side == "most" else "restrict-card-least"
    return f"""<div class="restrict-card {cls}">
  <div>
    <div class="restrict-card-name">{filename}</div>
    <div class="restrict-card-brand">{brand}</div>
  </div>
  {access_score_badge(score)}
</div>"""
