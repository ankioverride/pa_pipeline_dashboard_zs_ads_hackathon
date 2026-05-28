import streamlit as st

from utils.data_loader import (
    load_data,
    COL_FILENAME, COL_BRAND, COL_AGE, COL_STEP_TEXT,
    COL_STEPS_BRAND, COL_STEPS_GENERIC, COL_PHOTOTHERAPY,
    COL_TB, COL_QL, COL_SPECIALIST, COL_INIT_AUTH,
    COL_REAUTH_DUR, COL_REAUTH_REQ, COL_REAUTH_TEXT, COL_ACCESS,
)
from utils.styling import inject_css, NAVY

st.set_page_config(
    page_title="Policy Drilldown",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

df_all = load_data()

# ── Page header ───────────────────────────────────────────────────────────────
st.title("Policy Drilldown")
st.caption("Search and inspect individual payer policies")

# ── Search bar ────────────────────────────────────────────────────────────────
search_query = st.text_input("Search by Filename or Brand", placeholder="e.g. TREMFYA or 330109")

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")

all_brands = sorted(df_all[COL_BRAND].unique().tolist())
sel_brands = st.sidebar.multiselect("Brand", all_brands, default=all_brands)

score_buckets = sorted(df_all[COL_ACCESS].unique().tolist())
sel_scores = st.sidebar.multiselect(
    "Access Score",
    [str(s) for s in score_buckets],
    default=[str(s) for s in score_buckets],
)

age_opts = sorted(df_all[COL_AGE].unique().tolist())
sel_ages = st.sidebar.multiselect("Age", age_opts, default=age_opts)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_all.copy()

if search_query.strip():
    q = search_query.strip().lower()
    mask = (
        df[COL_FILENAME].str.lower().str.contains(q, na=False)
        | df[COL_BRAND].str.lower().str.contains(q, na=False)
    )
    df = df[mask]

if sel_brands:
    df = df[df[COL_BRAND].isin(sel_brands)]

if sel_scores:
    sel_scores_int = [int(s) for s in sel_scores]
    df = df[df[COL_ACCESS].isin(sel_scores_int)]

if sel_ages:
    df = df[df[COL_AGE].isin(sel_ages)]

# ── Filtered table ────────────────────────────────────────────────────────────
TABLE_COLS = [
    COL_FILENAME, COL_BRAND, COL_AGE, COL_ACCESS,
    COL_STEPS_BRAND, COL_STEPS_GENERIC, COL_PHOTOTHERAPY,
    COL_TB, COL_INIT_AUTH, COL_REAUTH_DUR, COL_SPECIALIST,
]

col_cfg = {
    COL_FILENAME: st.column_config.TextColumn("Filename"),
    COL_BRAND: st.column_config.TextColumn("Brand"),
    COL_AGE: st.column_config.TextColumn("Age"),
    COL_ACCESS: st.column_config.NumberColumn("Access Score"),
    COL_STEPS_BRAND: st.column_config.TextColumn("# Brand Steps"),
    COL_STEPS_GENERIC: st.column_config.TextColumn("# Generic Steps"),
    COL_PHOTOTHERAPY: st.column_config.TextColumn("Phototherapy"),
    COL_TB: st.column_config.TextColumn("TB"),
    COL_INIT_AUTH: st.column_config.TextColumn("Init Auth (months)"),
    COL_REAUTH_DUR: st.column_config.TextColumn("Reauth Dur (months)"),
    COL_SPECIALIST: st.column_config.TextColumn("Specialist"),
}

st.dataframe(
    df[TABLE_COLS].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    column_config=col_cfg,
)

st.markdown(f"**{len(df)} row(s) shown**")

# ── Row selector ──────────────────────────────────────────────────────────────
if df.empty:
    st.info("No rows match the current filters.")
    st.stop()

options = [
    f"{row[COL_FILENAME]} — {row[COL_BRAND]}"
    for _, row in df.iterrows()
]
selected_label = st.selectbox("Select a policy to inspect", options)

sel_idx = options.index(selected_label)
row = df.iloc[sel_idx]

# ── Detail panel ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"📄 **Source: {row[COL_FILENAME]}**")

LONG_TEXT_COLS = {COL_STEP_TEXT, COL_QL, COL_REAUTH_TEXT}
ALL_15 = [
    COL_FILENAME, COL_BRAND, COL_AGE, COL_STEP_TEXT,
    COL_STEPS_BRAND, COL_STEPS_GENERIC, COL_PHOTOTHERAPY,
    COL_TB, COL_QL, COL_SPECIALIST, COL_INIT_AUTH,
    COL_REAUTH_DUR, COL_REAUTH_REQ, COL_REAUTH_TEXT, COL_ACCESS,
]
FRIENDLY = {
    COL_FILENAME: "Filename",
    COL_BRAND: "Brand",
    COL_AGE: "Age",
    COL_STEP_TEXT: "Step Therapy Requirements",
    COL_STEPS_BRAND: "# Steps through Brands",
    COL_STEPS_GENERIC: "# Steps through Generic",
    COL_PHOTOTHERAPY: "Step through Phototherapy",
    COL_TB: "TB Test Required",
    COL_QL: "Quantity Limits",
    COL_SPECIALIST: "Specialist Types",
    COL_INIT_AUTH: "Init Auth (months)",
    COL_REAUTH_DUR: "Reauth Duration (months)",
    COL_REAUTH_REQ: "Reauth Required",
    COL_REAUTH_TEXT: "Reauth Requirements",
    COL_ACCESS: "Access Score",
}

short_cols = [c for c in ALL_15 if c not in LONG_TEXT_COLS]
col_a, col_b = st.columns(2)

for i, col in enumerate(short_cols):
    label = FRIENDLY.get(col, col)
    val = str(row[col])
    target = col_a if i % 2 == 0 else col_b
    with target:
        st.markdown(
            f'<p style="color:#888;font-size:12px;margin-bottom:2px">{label}</p>'
            f'<p style="color:{NAVY};font-weight:700;margin-top:0">{val}</p>',
            unsafe_allow_html=True,
        )

for col in LONG_TEXT_COLS:
    label = FRIENDLY.get(col, col)
    val = str(row[col])
    st.markdown(f"**{label}**")
    st.code(val, language=None)
