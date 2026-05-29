import streamlit as st
import pandas as pd

from utils.data_loader import (
    load_data,
    COL_FILENAME, COL_BRAND, COL_AGE, COL_STEP_TEXT,
    COL_STEPS_BRAND, COL_STEPS_GENERIC, COL_PHOTOTHERAPY,
    COL_TB, COL_QL, COL_SPECIALIST, COL_INIT_AUTH,
    COL_REAUTH_DUR, COL_REAUTH_REQ, COL_REAUTH_TEXT, COL_ACCESS,
)
from utils.styling import (
    inject_css, NAVY, section_header, access_score_badge,
    yes_no_badge, SCORE_BG, SCORE_COLORS,
)

df_all = load_data()

st.markdown(section_header("Policy Drilldown", "Search and inspect individual payer policies"), unsafe_allow_html=True)

# ── Search ────────────────────────────────────────────────────────────────────
search_query = st.text_input(
    "", placeholder="🔍   Search by Filename or Brand  (e.g. TREMFYA or 330109)",
    label_visibility="collapsed",
)

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.markdown("## Filters")

all_brands = sorted(df_all[COL_BRAND].unique().tolist())
sel_brands = st.sidebar.multiselect("Brand", all_brands, default=all_brands)

score_buckets = sorted(df_all[COL_ACCESS].unique().tolist())
sel_scores = st.sidebar.multiselect(
    "Access Score", [str(s) for s in score_buckets], default=[str(s) for s in score_buckets],
)

age_opts = sorted(df_all[COL_AGE].unique().tolist())
sel_ages = st.sidebar.multiselect("Age", age_opts, default=age_opts)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_all.copy()
if search_query.strip():
    q = search_query.strip().lower()
    df = df[
        df[COL_FILENAME].str.lower().str.contains(q, na=False)
        | df[COL_BRAND].str.lower().str.contains(q, na=False)
    ]
if sel_brands:
    df = df[df[COL_BRAND].isin(sel_brands)]
if sel_scores:
    df = df[df[COL_ACCESS].isin([int(s) for s in sel_scores])]
if sel_ages:
    df = df[df[COL_AGE].isin(sel_ages)]

# ── Result count ──────────────────────────────────────────────────────────────
st.markdown(f'<span class="result-badge">🔎 {len(df)} policies found</span>', unsafe_allow_html=True)

# ── Table ─────────────────────────────────────────────────────────────────────
TABLE_COLS = [
    COL_FILENAME, COL_BRAND, COL_AGE, COL_ACCESS,
    COL_STEPS_BRAND, COL_STEPS_GENERIC, COL_PHOTOTHERAPY,
    COL_TB, COL_INIT_AUTH, COL_REAUTH_DUR, COL_SPECIALIST,
]
col_cfg = {
    COL_FILENAME: st.column_config.TextColumn("Filename"),
    COL_BRAND: st.column_config.TextColumn("Brand"),
    COL_AGE: st.column_config.TextColumn("Age"),
    COL_ACCESS: st.column_config.NumberColumn("Access Score", format="%d"),
    COL_STEPS_BRAND: st.column_config.TextColumn("# Brand Steps"),
    COL_STEPS_GENERIC: st.column_config.TextColumn("# Generic Steps"),
    COL_PHOTOTHERAPY: st.column_config.TextColumn("Phototherapy"),
    COL_TB: st.column_config.TextColumn("TB Test"),
    COL_INIT_AUTH: st.column_config.TextColumn("Init Auth (months)"),
    COL_REAUTH_DUR: st.column_config.TextColumn("Reauth Dur (months)"),
    COL_SPECIALIST: st.column_config.TextColumn("Specialist"),
}

display_df = df[TABLE_COLS].reset_index(drop=True)


def _row_style(row):
    styles = [""] * len(TABLE_COLS)
    score = row[COL_ACCESS]
    idx = TABLE_COLS.index(COL_ACCESS)
    styles[idx] = (
        f"background-color: {SCORE_BG.get(score, '')};"
        f"color: {SCORE_COLORS.get(score, NAVY)}; font-weight: 700;"
    )
    return styles


styled = display_df.style.apply(_row_style, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True, column_config=col_cfg)

# ── Row selector ──────────────────────────────────────────────────────────────
if df.empty:
    st.info("No policies match the current filters.")
    st.stop()

options = [f"{r[COL_FILENAME]} — {r[COL_BRAND]}" for _, r in df.iterrows()]
selected_label = st.selectbox("Select a policy to inspect", options)
row = df.iloc[options.index(selected_label)]

# ── Policy Card ───────────────────────────────────────────────────────────────
score = int(row[COL_ACCESS])
st.markdown(f"""
<div class="policy-card">
  <div class="policy-card-header">
    <div>
      <div class="policy-card-header-title">📄 {row[COL_FILENAME]}</div>
      <div class="policy-card-header-sub">{row[COL_BRAND]}</div>
    </div>
    <div>{access_score_badge(score)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

LONG_TEXT_COLS = {COL_STEP_TEXT, COL_QL, COL_REAUTH_TEXT}
FRIENDLY = {
    COL_FILENAME: "Filename", COL_BRAND: "Brand", COL_AGE: "Age",
    COL_STEPS_BRAND: "# Steps through Brands", COL_STEPS_GENERIC: "# Steps through Generic",
    COL_PHOTOTHERAPY: "Step through Phototherapy", COL_TB: "TB Test Required",
    COL_SPECIALIST: "Specialist Types", COL_INIT_AUTH: "Init Auth (months)",
    COL_REAUTH_DUR: "Reauth Duration (months)", COL_REAUTH_REQ: "Reauth Required",
    COL_ACCESS: "Access Score",
    COL_STEP_TEXT: "Step Therapy Requirements",
    COL_QL: "Quantity Limits",
    COL_REAUTH_TEXT: "Reauthorization Requirements",
}

BADGE_COLS = {
    COL_TB: False,          # Yes = bad (more restrictive)
    COL_PHOTOTHERAPY: False,
    COL_REAUTH_REQ: False,
}

short_cols = [c for c in [
    COL_FILENAME, COL_BRAND, COL_AGE, COL_STEPS_BRAND,
    COL_STEPS_GENERIC, COL_PHOTOTHERAPY, COL_TB,
    COL_SPECIALIST, COL_INIT_AUTH, COL_REAUTH_DUR,
    COL_REAUTH_REQ, COL_ACCESS,
] if c not in LONG_TEXT_COLS]

col_a, col_b = st.columns(2)
for i, col in enumerate(short_cols):
    label = FRIENDLY.get(col, col)
    val = str(row[col])
    if col in BADGE_COLS:
        display_val = yes_no_badge(val, good_is_yes=BADGE_COLS[col])
    elif col == COL_ACCESS:
        display_val = access_score_badge(score)
    else:
        display_val = f'<span class="field-value">{val}</span>'

    html = (
        f'<div class="field-group">'
        f'<div class="field-label">{label}</div>'
        f'<div>{display_val}</div>'
        f'</div>'
    )
    (col_a if i % 2 == 0 else col_b).markdown(html, unsafe_allow_html=True)

# Long-text fields
for col in [COL_STEP_TEXT, COL_QL, COL_REAUTH_TEXT]:
    label = FRIENDLY.get(col, col)
    val = str(row[col])
    st.markdown(section_header(label), unsafe_allow_html=True)
    st.markdown(f'<div class="long-text-box">{val}</div>', unsafe_allow_html=True)

# ── Restrictiveness Scorecard ─────────────────────────────────────────────────
st.markdown(section_header("Restrictiveness Scorecard", "Policy-level summary"), unsafe_allow_html=True)

steps_total = int(row["steps_total_num"])
max_steps = int(df_all["steps_total_num"].max())
bar_pct = int(steps_total / max(max_steps, 1) * 100)

has_ql = row["has_ql"]

st.markdown(f"""
<div style="background:#F8F9FB;border-radius:10px;padding:20px 24px;margin-top:4px">
  <div style="margin-bottom:16px">
    <div class="field-label">Step Burden — {steps_total} of {max_steps} max steps</div>
    <div class="scorecard-bar-bg" style="margin-top:8px">
      <div class="scorecard-bar-fill" style="width:{bar_pct}%"></div>
    </div>
  </div>
  <div style="display:flex;gap:28px;flex-wrap:wrap;align-items:center">
    <div><span style="margin-right:6px">🩺 TB Test</span>{yes_no_badge(str(row[COL_TB]), good_is_yes=False)}</div>
    <div><span style="margin-right:6px">☀️ Phototherapy</span>{yes_no_badge(str(row[COL_PHOTOTHERAPY]), good_is_yes=False)}</div>
    <div><span style="margin-right:6px">📦 Qty Limits</span>{yes_no_badge("Yes" if has_ql else "No", good_is_yes=False)}</div>
    <div><span style="margin-right:6px">🔄 Reauth Required</span>{yes_no_badge(str(row[COL_REAUTH_REQ]), good_is_yes=False)}</div>
  </div>
</div>
""", unsafe_allow_html=True)
