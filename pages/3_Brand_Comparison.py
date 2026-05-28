import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.data_loader import (
    load_data,
    COL_BRAND, COL_AGE, COL_ACCESS, COL_TB, COL_QL,
    COL_SPECIALIST, COL_INIT_AUTH, COL_REAUTH_DUR,
    COL_STEPS_BRAND, COL_STEPS_GENERIC,
)
from utils.styling import inject_css, kpi_tile, NAVY, ORANGE

st.set_page_config(
    page_title="Brand Comparison",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

df_all = load_data()

st.title("Brand Comparison")
st.caption("Side-by-side restrictiveness analysis")

all_brands = sorted(df_all[COL_BRAND].unique().tolist())
default_left = "TREMFYA" if "TREMFYA" in all_brands else all_brands[0]
default_right = "STELARA" if "STELARA" in all_brands else (all_brands[1] if len(all_brands) > 1 else all_brands[0])

sel_col, _, ser_col = st.columns([2, 1, 2])
with sel_col:
    brand_left = st.selectbox("Left Brand", all_brands, index=all_brands.index(default_left))
with ser_col:
    brand_right = st.selectbox("Right Brand", all_brands, index=all_brands.index(default_right))

df_left = df_all[df_all[COL_BRAND] == brand_left]
df_right = df_all[df_all[COL_BRAND] == brand_right]

CHART_LAYOUT = dict(
    margin=dict(l=20, r=20, t=40, b=20),
    font=dict(family="Calibri, sans-serif", color=NAVY),
    template="simple_white",
)
CHART_CONFIG = {"displayModeBar": False}


def safe_mean(series) -> float:
    return series.mean() if len(series) > 0 else 0.0


def pct_yes(series) -> float:
    return (series == "Yes").mean() * 100 if len(series) > 0 else 0.0


def avg_steps(df) -> float:
    return df["steps_total_num"].mean() if len(df) > 0 else 0.0


def pct_ql(df) -> float:
    return df["has_ql"].mean() * 100 if len(df) > 0 else 0.0


def arrow(left_val, right_val, higher_is_better=True) -> str:
    if left_val == right_val:
        return "→"
    if higher_is_better:
        return "↑" if left_val > right_val else "↓"
    return "↑" if left_val < right_val else "↓"


# ── Headline KPIs ─────────────────────────────────────────────────────────────
st.markdown("---")
k1, k2, k3, k4 = st.columns(4)

avg_l = round(safe_mean(df_left[COL_ACCESS]))
avg_r = round(safe_mean(df_right[COL_ACCESS]))
steps_l = round(avg_steps(df_left), 1)
steps_r = round(avg_steps(df_right), 1)
tb_l = round(pct_yes(df_left[COL_TB]))
tb_r = round(pct_yes(df_right[COL_TB]))
ql_l = round(pct_ql(df_left))
ql_r = round(pct_ql(df_right))

with k1:
    st.markdown(kpi_tile(f"Avg Access Score", f"{avg_l} {arrow(avg_l, avg_r)} {avg_r}"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_tile("Avg # Steps", f"{steps_l} {arrow(steps_l, steps_r, False)} {steps_r}"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_tile("% requiring TB", f"{tb_l}% {arrow(tb_l, tb_r, False)} {tb_r}%"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_tile("% with QL", f"{ql_l}% {arrow(ql_l, ql_r, False)} {ql_r}%"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Helper: grouped bar chart ─────────────────────────────────────────────────
def grouped_bar(title, x_vals_l, x_vals_r, x_label=""):
    counts_l = pd.Series(x_vals_l).value_counts().reindex(
        sorted(set(x_vals_l) | set(x_vals_r)), fill_value=0
    )
    counts_r = pd.Series(x_vals_r).value_counts().reindex(counts_l.index, fill_value=0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=brand_left, x=counts_l.index.astype(str), y=counts_l.values,
        marker_color=NAVY,
    ))
    fig.add_trace(go.Bar(
        name=brand_right, x=counts_r.index.astype(str), y=counts_r.values,
        marker_color=ORANGE,
    ))
    fig.update_layout(
        barmode="group",
        title=title,
        xaxis_title=x_label,
        yaxis_title="# Policies",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_LAYOUT,
    )
    return fig


# ── 2×2 chart grid ────────────────────────────────────────────────────────────
row1_left, row1_right = st.columns(2)

with row1_left:
    fig_age = grouped_bar(
        "Age Distribution",
        df_left[COL_AGE].tolist(),
        df_right[COL_AGE].tolist(),
        x_label="Age Category",
    )
    st.plotly_chart(fig_age, use_container_width=True, config=CHART_CONFIG)

with row1_right:
    init_l = df_left[COL_INIT_AUTH].astype(str).tolist()
    init_r = df_right[COL_INIT_AUTH].astype(str).tolist()
    fig_init = grouped_bar("Initial Auth Duration", init_l, init_r, x_label="Months / Status")
    st.plotly_chart(fig_init, use_container_width=True, config=CHART_CONFIG)

row2_left, row2_right = st.columns(2)

with row2_left:
    reauth_l = df_left[COL_REAUTH_DUR].astype(str).tolist()
    reauth_r = df_right[COL_REAUTH_DUR].astype(str).tolist()
    fig_reauth = grouped_bar("Reauth Duration", reauth_l, reauth_r, x_label="Months / Status")
    st.plotly_chart(fig_reauth, use_container_width=True, config=CHART_CONFIG)

with row2_right:
    all_step_vals = sorted(
        set(df_left["steps_brand_num"].tolist() + df_right["steps_brand_num"].tolist()
            + df_left["steps_generic_num"].tolist() + df_right["steps_generic_num"].tolist())
    )
    all_x = sorted(set(
        df_left["steps_total_num"].astype(str).tolist()
        + df_right["steps_total_num"].astype(str).tolist()
    ), key=lambda v: int(v))

    brand_steps_l = df_left["steps_brand_num"].value_counts()
    generic_steps_l = df_left["steps_generic_num"].value_counts()
    brand_steps_r = df_right["steps_brand_num"].value_counts()
    generic_steps_r = df_right["steps_generic_num"].value_counts()

    step_x_l = sorted(df_left["steps_total_num"].unique())
    step_x_r = sorted(df_right["steps_total_num"].unique())
    all_step_x = sorted(set(step_x_l + step_x_r))

    fig_steps = go.Figure()
    for brand_name, dset, color_brand, color_gen in [
        (brand_left, df_left, NAVY, "#3A5A8C"),
        (brand_right, df_right, ORANGE, "#FAA85F"),
    ]:
        x_str = [str(v) for v in all_step_x]
        brand_counts = dset["steps_brand_num"].value_counts().reindex(all_step_x, fill_value=0)
        generic_counts = dset["steps_generic_num"].value_counts().reindex(all_step_x, fill_value=0)
        fig_steps.add_trace(go.Bar(
            name=f"{brand_name} — Brand Steps",
            x=x_str, y=brand_counts.values, marker_color=color_brand,
        ))
        fig_steps.add_trace(go.Bar(
            name=f"{brand_name} — Generic Steps",
            x=x_str, y=generic_counts.values, marker_color=color_gen,
        ))

    fig_steps.update_layout(
        barmode="stack",
        title="Step Count Distribution",
        xaxis_title="Total Steps",
        yaxis_title="# Policies",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_steps, use_container_width=True, config=CHART_CONFIG)

# ── Restrictiveness gap table ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("Restrictiveness Parameter Gap")


def mode_val(series) -> str:
    vc = series.value_counts()
    return str(vc.index[0]) if len(vc) > 0 else "—"


params = [
    ("Age", df_left[COL_AGE], df_right[COL_AGE]),
    ("# Steps (total)", df_left["steps_total_num"].astype(str), df_right["steps_total_num"].astype(str)),
    ("TB Test", df_left[COL_TB], df_right[COL_TB]),
    ("Quantity Limits", df_left["has_ql"].map({True: "Yes", False: "No"}), df_right["has_ql"].map({True: "Yes", False: "No"})),
    ("Specialist", df_left[COL_SPECIALIST], df_right[COL_SPECIALIST]),
    ("Init Auth (months)", df_left[COL_INIT_AUTH], df_right[COL_INIT_AUTH]),
    ("Reauth Duration (months)", df_left[COL_REAUTH_DUR], df_right[COL_REAUTH_DUR]),
]

gap_rows = []
for param, l_series, r_series in params:
    l_val = mode_val(l_series)
    r_val = mode_val(r_series)
    gap_rows.append({
        "Parameter": param,
        brand_left: l_val,
        brand_right: r_val,
        "Gap": "✓" if l_val == r_val else "⚠",
    })

df_gap = pd.DataFrame(gap_rows)


def highlight_gap(row):
    if row["Gap"] == "⚠":
        return ["background-color: #FFF3E0"] * len(row)
    return [""] * len(row)


styled = df_gap.style.apply(highlight_gap, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)
