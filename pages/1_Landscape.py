import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.data_loader import (
    load_data, COL_BRAND, COL_ACCESS, COL_TB, COL_QL,
    COL_SPECIALIST, COL_FILENAME, COL_REAUTH_REQ,
)
from utils.styling import (
    inject_css, NAVY, ORANGE, NAVY_SEQ,
    hero_banner, stat_card, section_header, restrict_card,
    SCORE_COLORS, SCORE_BG,
)

df_all = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Filters")

all_brands = sorted(df_all[COL_BRAND].unique().tolist())
selected_brands = st.sidebar.multiselect("Brand", all_brands, default=all_brands)

score_range = st.sidebar.slider(
    "Access Score range", min_value=0, max_value=100, value=(0, 100), step=25,
)

step_filter = st.sidebar.selectbox(
    "Step Therapy", ["All", "Has step therapy", "No step therapy"], index=0,
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

# ── Hero Banner ───────────────────────────────────────────────────────────────
total = len(df)
n_brands = df[COL_BRAND].nunique()
avg_score = round(df[COL_ACCESS].mean(), 1) if total > 0 else 0
pct_step = round(df["has_step_therapy"].mean() * 100) if total > 0 else 0
pct_tb = round((df[COL_TB] == "Yes").mean() * 100) if total > 0 else 0
pct_reauth = round((df[COL_REAUTH_REQ] == "Yes").mean() * 100) if total > 0 else 0

st.markdown(
    hero_banner(
        "Payer PA Policy Intelligence",
        "Plaque Psoriasis · Prior Authorization Policy Landscape",
        [
            {"num": str(total), "label": "Policies"},
            {"num": str(n_brands), "label": "Brands"},
            {"num": str(avg_score), "label": "Avg Access Score"},
            {"num": f"{pct_step}%", "label": "Step Therapy"},
            {"num": f"{pct_tb}%", "label": "TB Test Req"},
            {"num": f"{pct_reauth}%", "label": "Reauth Req"},
        ],
    ),
    unsafe_allow_html=True,
)

# ── 6 Stat Cards ─────────────────────────────────────────────────────────────
all_avg = round(df_all[COL_ACCESS].mean(), 1)
score_delta = round(avg_score - all_avg, 1) if total > 0 else 0
delta_type = "good" if score_delta >= 0 else "bad"
delta_str = f"{'↑' if score_delta >= 0 else '↓'} {abs(score_delta)} vs all"

c1, c2, c3, c4, c5, c6 = st.columns(6)
cards = [
    (c1, "📋", "Total Policies", str(total), None, "neutral"),
    (c2, "💊", "Brands Covered", str(n_brands), None, "neutral"),
    (c3, "⭐", "Avg Access Score", str(avg_score), delta_str, delta_type),
    (c4, "🔗", "% Step Therapy", f"{pct_step}%", None, "neutral"),
    (c5, "🩺", "% TB Test Req", f"{pct_tb}%", None, "neutral"),
    (c6, "🔄", "% Requiring Reauth", f"{pct_reauth}%", None, "neutral"),
]
for col, icon, label, value, delta, dtype in cards:
    with col:
        st.markdown(stat_card(icon, label, value, delta, dtype), unsafe_allow_html=True)

CHART_LAYOUT = dict(
    template="simple_white",
    margin=dict(l=20, r=20, t=44, b=20),
    font=dict(family="Calibri, sans-serif", color=NAVY),
    plot_bgcolor="#FAFBFC",
    paper_bgcolor="white",
    hoverlabel=dict(bgcolor="white", bordercolor=NAVY, font_size=13),
    height=400,
)
CHART_CONFIG = {"displayModeBar": False}

# ── Section: Score Distribution + Heatmap ─────────────────────────────────────
st.markdown(section_header("Access Score Landscape", "Distribution and brand-level breakdown"), unsafe_allow_html=True)

col_donut, col_heat = st.columns([1, 1.5])

with col_donut:
    bucket_counts = (
        df.groupby(COL_ACCESS).size()
        .reindex([50, 75, 100], fill_value=0)
        .reset_index(name="count")
    )
    fig_donut = go.Figure(go.Pie(
        labels=bucket_counts[COL_ACCESS].astype(str),
        values=bucket_counts["count"],
        hole=0.56,
        marker=dict(colors=[SCORE_COLORS[s] for s in [50, 75, 100]], line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(size=13),
        hovertemplate="Score %{label}<br>%{value} policies<extra></extra>",
    ))
    fig_donut.add_annotation(
        text="Access<br>Score", x=0.5, y=0.5, showarrow=False,
        font=dict(size=13, color=NAVY, family="Calibri, sans-serif"),
    )
    fig_donut.update_layout(title="Access Score Distribution", showlegend=True,
                            legend=dict(orientation="h", y=-0.08), **CHART_LAYOUT)
    st.plotly_chart(fig_donut, use_container_width=True, config=CHART_CONFIG)

with col_heat:
    pivot = df.groupby([COL_BRAND, COL_ACCESS]).size().unstack(fill_value=0)
    for sc in [50, 75, 100]:
        if sc not in pivot.columns:
            pivot[sc] = 0
    pivot = pivot[[50, 75, 100]]
    brands_sorted = pivot.sum(axis=1).sort_values(ascending=True).index.tolist()
    pivot = pivot.loc[brands_sorted]
    z = pivot.values.tolist()
    fig_heat = go.Figure(go.Heatmap(
        z=z,
        x=["50", "75", "100"],
        y=brands_sorted,
        colorscale=[[0, "#EEF2F8"], [0.5, "#3A5A8C"], [1.0, "#1B365D"]],
        text=[[str(v) for v in row] for row in z],
        texttemplate="%{text}",
        hovertemplate="Brand: %{y}<br>Score: %{x}<br>Count: %{z}<extra></extra>",
        showscale=False,
        zmin=0,
    ))
    fig_heat.update_layout(
        title="Policy Count by Brand × Access Score",
        xaxis_title="Access Score",
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_heat, use_container_width=True, config=CHART_CONFIG)

# ── Section: Brand Landscape Bubble Chart ─────────────────────────────────────
st.markdown(section_header("Brand Landscape", "Average steps vs access score — bubble size = policy count"), unsafe_allow_html=True)

bubble = (
    df.groupby(COL_BRAND)
    .agg(avg_steps=("steps_total_num", "mean"), avg_access=(COL_ACCESS, "mean"), count=(COL_BRAND, "size"))
    .reset_index()
)
colors = (NAVY_SEQ * 4)[:len(bubble)]
fig_bubble = go.Figure(go.Scatter(
    x=bubble["avg_steps"],
    y=bubble["avg_access"],
    mode="markers+text",
    text=bubble[COL_BRAND],
    textposition="top center",
    textfont=dict(size=11, color=NAVY),
    marker=dict(
        size=bubble["count"] * 7,
        color=colors,
        opacity=0.82,
        line=dict(width=1.5, color="white"),
    ),
    hovertemplate=(
        "<b>%{text}</b><br>Avg Steps: %{x:.1f}<br>"
        "Avg Access Score: %{y:.1f}<extra></extra>"
    ),
))
mean_steps = df["steps_total_num"].mean()
mean_access = df[COL_ACCESS].mean()
fig_bubble.add_vline(x=mean_steps, line_dash="dash", line_color=ORANGE, opacity=0.6,
                     annotation_text="Avg Steps", annotation_position="top right")
fig_bubble.add_hline(y=mean_access, line_dash="dash", line_color=NAVY, opacity=0.4,
                     annotation_text="Avg Score", annotation_position="bottom right")
fig_bubble.update_layout(
    title="Brand Landscape: Avg Steps vs Access Score",
    xaxis_title="Average Total Steps",
    yaxis_title="Average Access Score",
    height=440,
    **{k: v for k, v in CHART_LAYOUT.items() if k != "height"},
)
st.plotly_chart(fig_bubble, use_container_width=True, config=CHART_CONFIG)

# ── Section: Restrictiveness Components ───────────────────────────────────────
st.markdown(section_header("Restrictiveness by Brand", "% of policies with each restriction type"), unsafe_allow_html=True)

grp = (
    df.groupby(COL_BRAND)
    .agg(
        pct_step=("has_step_therapy", lambda x: round(x.mean() * 100, 1)),
        pct_tb=(COL_TB, lambda x: round((x == "Yes").mean() * 100, 1)),
        pct_ql=("has_ql", lambda x: round(x.mean() * 100, 1)),
    )
    .reset_index()
    .sort_values("pct_step", ascending=False)
)

fig_grp = go.Figure()
for metric, color, name in [
    ("pct_step", NAVY, "Step Therapy"),
    ("pct_tb", ORANGE, "TB Test"),
    ("pct_ql", "#6B89B5", "Qty Limits"),
]:
    fig_grp.add_trace(go.Bar(
        name=name,
        x=grp[COL_BRAND],
        y=grp[metric],
        marker_color=color,
        text=grp[metric].apply(lambda v: f"{int(v)}%"),
        textposition="outside",
        textfont=dict(size=10),
        hovertemplate=f"{name}: %{{y:.1f}}%<extra></extra>",
    ))
fig_grp.update_layout(
    barmode="group",
    title="Restrictiveness Components by Brand",
    xaxis_title="",
    yaxis_title="% of Policies",
    yaxis=dict(range=[0, 115]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    **CHART_LAYOUT,
)
st.plotly_chart(fig_grp, use_container_width=True, config=CHART_CONFIG)

# ── Section: Policy Count per Brand ───────────────────────────────────────────
col_count, col_spacer = st.columns([1.6, 1])

with col_count:
    brand_counts = df.groupby(COL_BRAND).size().reset_index(name="count").sort_values("count", ascending=True)
    bar_colors = (NAVY_SEQ * 4)[:len(brand_counts)]
    fig_count = go.Figure(go.Bar(
        y=brand_counts[COL_BRAND],
        x=brand_counts["count"],
        orientation="h",
        marker_color=bar_colors,
        text=brand_counts["count"],
        textposition="outside",
        hovertemplate="%{y}: %{x} policies<extra></extra>",
    ))
    fig_count.update_layout(
        title="Policy Count by Brand",
        xaxis_title="Number of Policies",
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_count, use_container_width=True, config=CHART_CONFIG)

with col_spacer:
    # Avg access score per brand (ranked)
    brand_avg = (
        df.groupby(COL_BRAND)[COL_ACCESS].mean()
        .reset_index(name="avg_score")
        .sort_values("avg_score", ascending=True)
    )
    fig_avg = go.Figure(go.Bar(
        y=brand_avg[COL_BRAND],
        x=brand_avg["avg_score"],
        orientation="h",
        marker_color=ORANGE,
        text=brand_avg["avg_score"].round().astype(int),
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}<extra></extra>",
    ))
    fig_avg.update_layout(
        title="Avg Access Score by Brand",
        xaxis_title="Avg Score",
        xaxis=dict(range=[0, 120]),
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_avg, use_container_width=True, config=CHART_CONFIG)

# ── Section: Policy Spotlight ─────────────────────────────────────────────────
st.markdown(section_header("Policy Spotlight", "5 most & least restrictive policies"), unsafe_allow_html=True)

show_cols = [COL_FILENAME, COL_BRAND, COL_ACCESS]
most_5 = df[show_cols].sort_values(COL_ACCESS, ascending=True).head(5)
least_5 = df[show_cols].sort_values(COL_ACCESS, ascending=False).head(5)

col_most, col_least = st.columns(2)

with col_most:
    st.markdown("**Most Restrictive**")
    cards_html = "".join(
        restrict_card(row[COL_FILENAME], row[COL_BRAND], int(row[COL_ACCESS]), "most")
        for _, row in most_5.iterrows()
    )
    st.markdown(cards_html, unsafe_allow_html=True)

with col_least:
    st.markdown("**Least Restrictive**")
    cards_html = "".join(
        restrict_card(row[COL_FILENAME], row[COL_BRAND], int(row[COL_ACCESS]), "least")
        for _, row in least_5.iterrows()
    )
    st.markdown(cards_html, unsafe_allow_html=True)
