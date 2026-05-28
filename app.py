import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import (
    load_data, COL_BRAND, COL_ACCESS, COL_TB, COL_QL, COL_SPECIALIST,
    COL_FILENAME,
)
from utils.styling import inject_css, kpi_tile, NAVY, ORANGE, NAVY_SEQ

st.set_page_config(
    page_title="Payer PA Policy Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

df_all = load_data()

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.header("Filters")

all_brands = sorted(df_all[COL_BRAND].unique().tolist())
selected_brands = st.sidebar.multiselect("Brand", all_brands, default=all_brands)

score_range = st.sidebar.slider(
    "Access Score range", min_value=0, max_value=100, value=(0, 100), step=25
)

step_filter = st.sidebar.selectbox(
    "Step Therapy presence",
    ["All", "Has step therapy", "No step therapy"],
    index=0,
)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_all.copy()
if selected_brands:
    df = df[df[COL_BRAND].isin(selected_brands)]
df = df[df[COL_ACCESS].between(score_range[0], score_range[1])]
if step_filter == "Has step therapy":
    df = df[df["has_step_therapy"]]
elif step_filter == "No step therapy":
    df = df[~df["has_step_therapy"]]

# ── Page header ───────────────────────────────────────────────────────────────
st.title("Payer PA Policy Intelligence")
st.caption("Plaque Psoriasis access landscape across 79 payer policies")

# ── KPI tiles ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

total = len(df)
avg_score = round(df[COL_ACCESS].mean()) if total > 0 else 0
pct_step = f"{round(df['has_step_therapy'].mean() * 100)}%" if total > 0 else "—"
pct_tb = f"{round((df[COL_TB] == 'Yes').mean() * 100)}%" if total > 0 else "—"

with k1:
    st.markdown(kpi_tile("Total Policies", str(total)), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_tile("Avg Access Score", str(avg_score) if total > 0 else "—"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_tile("% with Step Therapy", pct_step), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_tile("% requiring TB Test", pct_tb), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Two side-by-side charts ───────────────────────────────────────────────────
col_left, col_right = st.columns(2)

CHART_LAYOUT = dict(
    margin=dict(l=20, r=20, t=40, b=20),
    font=dict(family="Calibri, sans-serif", color=NAVY),
    template="simple_white",
)
CHART_CONFIG = {"displayModeBar": False}

with col_left:
    bucket_counts = (
        df.groupby(COL_ACCESS)
        .size()
        .reindex([0, 25, 50, 75, 100], fill_value=0)
        .reset_index(name="count")
    )
    bucket_counts[COL_ACCESS] = bucket_counts[COL_ACCESS].astype(str)

    fig_dist = go.Figure(
        go.Bar(
            x=bucket_counts[COL_ACCESS],
            y=bucket_counts["count"],
            marker_color=NAVY,
            text=bucket_counts["count"],
            textposition="outside",
        )
    )
    fig_dist.update_layout(
        title="Access Score distribution",
        xaxis=dict(categoryorder="array", categoryarray=["0", "25", "50", "75", "100"]),
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_dist, use_container_width=True, config=CHART_CONFIG)

with col_right:
    brand_avg = (
        df.groupby(COL_BRAND)[COL_ACCESS]
        .mean()
        .reset_index(name="avg_score")
        .sort_values("avg_score", ascending=True)
    )
    brand_avg["label"] = brand_avg["avg_score"].round().astype(int).astype(str)

    fig_brand = go.Figure(
        go.Bar(
            y=brand_avg[COL_BRAND],
            x=brand_avg["avg_score"],
            orientation="h",
            marker_color=ORANGE,
            text=brand_avg["label"],
            textposition="outside",
        )
    )
    fig_brand.update_layout(
        title="Average Access Score by Brand",
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_brand, use_container_width=True, config=CHART_CONFIG)

# ── Restrictiveness mix stacked bar ──────────────────────────────────────────
st.markdown("---")

restrict_rows = []
for brand, grp in df.groupby(COL_BRAND):
    n = len(grp)
    if n == 0:
        continue
    restrict_rows.append({
        "Brand": brand,
        "Step Therapy": round(grp["has_step_therapy"].mean() * 100, 1),
        "TB Test": round((grp[COL_TB] == "Yes").mean() * 100, 1),
        "Quantity Limits": round(grp["has_ql"].mean() * 100, 1),
        "Specialist Req": round((~grp[COL_SPECIALIST].isin(["NA", ""])).mean() * 100, 1),
    })

if restrict_rows:
    import pandas as pd
    df_restrict = pd.DataFrame(restrict_rows)
    categories = ["Step Therapy", "TB Test", "Quantity Limits", "Specialist Req"]

    fig_mix = go.Figure()
    for i, cat in enumerate(categories):
        fig_mix.add_trace(
            go.Bar(
                name=cat,
                y=df_restrict["Brand"],
                x=df_restrict[cat],
                orientation="h",
                marker_color=NAVY_SEQ[i % len(NAVY_SEQ)],
            )
        )

    fig_mix.update_layout(
        barmode="stack",
        title="Restrictiveness components by Brand",
        xaxis=dict(title="% of policies", range=[0, 100]),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_mix, use_container_width=True, config=CHART_CONFIG)

# ── Top / Bottom 5 tables ─────────────────────────────────────────────────────
st.markdown("---")
tbl_left, tbl_right = st.columns(2)

show_cols = [COL_FILENAME, COL_BRAND, COL_ACCESS]
sorted_asc = df[show_cols].sort_values(COL_ACCESS, ascending=True).head(5)
sorted_desc = df[show_cols].sort_values(COL_ACCESS, ascending=False).head(5)
sorted_asc[COL_ACCESS] = sorted_asc[COL_ACCESS].astype(int)
sorted_desc[COL_ACCESS] = sorted_desc[COL_ACCESS].astype(int)

with tbl_left:
    st.subheader("Top 5 Most Restrictive")
    st.dataframe(sorted_asc, use_container_width=True, hide_index=True)

with tbl_right:
    st.subheader("Top 5 Least Restrictive")
    st.dataframe(sorted_desc, use_container_width=True, hide_index=True)
