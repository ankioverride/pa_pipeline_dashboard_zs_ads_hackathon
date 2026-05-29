import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.data_loader import (
    load_data,
    COL_BRAND, COL_AGE, COL_ACCESS, COL_TB, COL_QL,
    COL_SPECIALIST, COL_INIT_AUTH, COL_REAUTH_DUR,
    COL_STEPS_BRAND, COL_STEPS_GENERIC,
)
from utils.styling import (
    inject_css, NAVY, ORANGE, NAVY_SEQ,
    section_header, access_score_badge, yes_no_badge,
)

df_all = load_data()

st.markdown(section_header("Brand Comparison", "Side-by-side restrictiveness analysis"), unsafe_allow_html=True)

# ── Brand selectors ───────────────────────────────────────────────────────────
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


def safe_pct(series, val):
    return round((series == val).mean() * 100, 1) if len(series) > 0 else 0.0


def safe_mean(series):
    return round(series.mean(), 1) if len(series) > 0 else 0.0


avg_l = safe_mean(df_left[COL_ACCESS])
avg_r = safe_mean(df_right[COL_ACCESS])
steps_l = safe_mean(df_left["steps_total_num"])
steps_r = safe_mean(df_right["steps_total_num"])
tb_l = safe_pct(df_left[COL_TB], "Yes")
tb_r = safe_pct(df_right[COL_TB], "Yes")
ql_l = round(df_left["has_ql"].mean() * 100, 1) if len(df_left) > 0 else 0.0
ql_r = round(df_right["has_ql"].mean() * 100, 1) if len(df_right) > 0 else 0.0
step_pct_l = round(df_left["has_step_therapy"].mean() * 100, 1) if len(df_left) > 0 else 0.0
step_pct_r = round(df_right["has_step_therapy"].mean() * 100, 1) if len(df_right) > 0 else 0.0

# ── Comparator header ─────────────────────────────────────────────────────────
avg_l_chip = access_score_badge(min([50, 75, 100], key=lambda x: abs(x - avg_l)))
avg_r_chip = access_score_badge(min([50, 75, 100], key=lambda x: abs(x - avg_r)))

st.markdown(f"""
<div style="display:flex;justify-content:center;align-items:center;gap:48px;
            padding:20px;background:#F8F9FB;border-radius:12px;margin:16px 0">
  <div style="text-align:center">
    <div style="font-size:22px;font-weight:700;color:#1B365D">{brand_left}</div>
    <div style="margin-top:6px">{avg_l_chip}</div>
    <div style="color:#9CA3AF;font-size:12px;margin-top:4px">{len(df_left)} policies</div>
  </div>
  <div style="font-size:32px;color:#D1D9E6">⚖️</div>
  <div style="text-align:center">
    <div style="font-size:22px;font-weight:700;color:#F37021">{brand_right}</div>
    <div style="margin-top:6px">{avg_r_chip}</div>
    <div style="color:#9CA3AF;font-size:12px;margin-top:4px">{len(df_right)} policies</div>
  </div>
</div>
""", unsafe_allow_html=True)

CHART_LAYOUT = dict(
    template="simple_white",
    margin=dict(l=20, r=20, t=44, b=20),
    font=dict(family="Calibri, sans-serif", color=NAVY),
    plot_bgcolor="#FAFBFC",
    paper_bgcolor="white",
    hoverlabel=dict(bgcolor="white", bordercolor=NAVY, font_size=13),
    height=380,
)
CHART_CONFIG = {"displayModeBar": False}


def win_card(metric_name, left_val, right_val, higher_is_better=True, fmt="{v}"):
    left_wins = (left_val > right_val) if higher_is_better else (left_val < right_val)
    tie = abs(left_val - right_val) < 0.01
    if tie:
        winner_html = '<div style="color:#9CA3AF;font-size:12px;margin-top:6px">Tied</div>'
    elif left_wins:
        winner_html = f'<div style="color:#1B365D;font-size:12px;font-weight:700;margin-top:6px">🏆 {brand_left}</div>'
    else:
        winner_html = f'<div style="color:#F37021;font-size:12px;font-weight:700;margin-top:6px">🏆 {brand_right}</div>'

    lv = fmt.format(v=left_val)
    rv = fmt.format(v=right_val)
    return f"""
<div style="background:#fff;border-radius:12px;padding:16px 12px;
            box-shadow:0 2px 10px rgba(27,54,93,0.08);text-align:center">
  <div style="font-size:10px;color:#9CA3AF;text-transform:uppercase;
              letter-spacing:0.8px;margin-bottom:10px">{metric_name}</div>
  <div style="display:flex;justify-content:center;align-items:center;gap:12px">
    <div style="font-size:20px;font-weight:700;color:#1B365D">{lv}</div>
    <div style="font-size:11px;color:#D1D9E6">vs</div>
    <div style="font-size:20px;font-weight:700;color:#F37021">{rv}</div>
  </div>
  {winner_html}
</div>"""


# ── Win/Loss row ──────────────────────────────────────────────────────────────
st.markdown(section_header("Head-to-Head Metrics", ""), unsafe_allow_html=True)
w1, w2, w3, w4, w5 = st.columns(5)
win_data = [
    (w1, "Avg Access Score", avg_l, avg_r, True, "{v}"),
    (w2, "Avg # Steps", steps_l, steps_r, False, "{v}"),
    (w3, "% TB Test", tb_l, tb_r, False, "{v}%"),
    (w4, "% Qty Limits", ql_l, ql_r, False, "{v}%"),
    (w5, "% Step Therapy", step_pct_l, step_pct_r, False, "{v}%"),
]
for col, name, lv, rv, higher, fmt in win_data:
    with col:
        st.markdown(win_card(name, lv, rv, higher, fmt), unsafe_allow_html=True)

# ── Radar Chart ───────────────────────────────────────────────────────────────
st.markdown(section_header("Access Profile Radar", "Normalized across all brands — outward = better access"), unsafe_allow_html=True)

brand_metrics = df_all.groupby(COL_BRAND).agg(
    avg_steps=("steps_total_num", "mean"),
    pct_tb=(COL_TB, lambda x: (x == "Yes").mean() * 100),
    pct_ql=("has_ql", lambda x: x.mean() * 100),
    pct_step=("has_step_therapy", lambda x: x.mean() * 100),
    avg_access=(COL_ACCESS, "mean"),
)


def normalize_invert(series):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([0.5] * len(series), index=series.index)
    return 1 - (series - mn) / (mx - mn)


def normalize(series):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - mn) / (mx - mn)


norm = pd.DataFrame({
    "Avg Steps": normalize_invert(brand_metrics["avg_steps"]),
    "% TB Test": normalize_invert(brand_metrics["pct_tb"]),
    "% Qty Limits": normalize_invert(brand_metrics["pct_ql"]),
    "% Step Therapy": normalize_invert(brand_metrics["pct_step"]),
    "Avg Access Score": normalize(brand_metrics["avg_access"]),
}, index=brand_metrics.index)

dims = list(norm.columns)

fig_radar = go.Figure()
for brand_name, color, fill_color in [
    (brand_left, NAVY, "rgba(27,54,93,0.15)"),
    (brand_right, ORANGE, "rgba(243,112,33,0.15)"),
]:
    if brand_name not in norm.index:
        continue
    vals = norm.loc[brand_name, dims].tolist()
    vals_closed = vals + [vals[0]]
    dims_closed = dims + [dims[0]]
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_closed, theta=dims_closed,
        fill="toself", fillcolor=fill_color,
        line=dict(color=color, width=2.5),
        name=brand_name,
        hovertemplate="%{theta}: %{r:.2f}<extra>" + brand_name + "</extra>",
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 1], showticklabels=False, gridcolor="#E5E7EB"),
        angularaxis=dict(gridcolor="#E5E7EB"),
    ),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    title="Access Profile Comparison (normalized — outward = better access)",
    **{k: v for k, v in CHART_LAYOUT.items() if k != "plot_bgcolor"},
)
st.plotly_chart(fig_radar, use_container_width=True, config=CHART_CONFIG)

# ── Age × Access Heatmaps ─────────────────────────────────────────────────────
st.markdown(section_header("Age × Access Score Distribution", "Policy breakdown per brand"), unsafe_allow_html=True)

hm_left, hm_right = st.columns(2)

for col_widget, brand_name, dset in [(hm_left, brand_left, df_left), (hm_right, brand_right, df_right)]:
    with col_widget:
        if dset.empty:
            st.info(f"No data for {brand_name}")
            continue
        ct = pd.crosstab(dset[COL_AGE], dset[COL_ACCESS])
        for sc in [50, 75, 100]:
            if sc not in ct.columns:
                ct[sc] = 0
        ct = ct[[50, 75, 100]]
        z = ct.values.tolist()
        fig_hm = go.Figure(go.Heatmap(
            z=z,
            x=["50", "75", "100"],
            y=ct.index.tolist(),
            colorscale=[[0, "#EEF2F8"], [0.5, "#3A5A8C"], [1.0, "#1B365D"]],
            text=[[str(v) for v in row] for row in z],
            texttemplate="%{text}",
            showscale=False,
            zmin=0,
            hovertemplate="Age: %{y}<br>Score: %{x}<br>Count: %{z}<extra></extra>",
        ))
        fig_hm.update_layout(
            title=f"{brand_name}: Age × Access Score",
            xaxis_title="Access Score",
            **CHART_LAYOUT,
        )
        st.plotly_chart(fig_hm, use_container_width=True, config=CHART_CONFIG)

# ── Distribution Charts 2×2 ───────────────────────────────────────────────────
st.markdown(section_header("Distribution Breakdown", "Age, auth duration, and step counts"), unsafe_allow_html=True)

row1_l, row1_r = st.columns(2)
row2_l, row2_r = st.columns(2)


def grouped_bar_fig(title, vals_l, vals_r, x_label=""):
    all_cats = sorted(set(vals_l + vals_r), key=lambda v: (str(v).isdigit(), v))
    counts_l = pd.Series(vals_l).value_counts().reindex(all_cats, fill_value=0)
    counts_r = pd.Series(vals_r).value_counts().reindex(all_cats, fill_value=0)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=brand_left, x=[str(c) for c in all_cats], y=counts_l.values,
        marker_color=NAVY, text=counts_l.values, textposition="outside",
        hovertemplate="%{x}: %{y}<extra>" + brand_left + "</extra>",
    ))
    fig.add_trace(go.Bar(
        name=brand_right, x=[str(c) for c in all_cats], y=counts_r.values,
        marker_color=ORANGE, text=counts_r.values, textposition="outside",
        hovertemplate="%{x}: %{y}<extra>" + brand_right + "</extra>",
    ))
    fig.update_layout(
        barmode="group", title=title, xaxis_title=x_label, yaxis_title="# Policies",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_LAYOUT,
    )
    return fig


with row1_l:
    st.plotly_chart(grouped_bar_fig("Age Distribution", df_left[COL_AGE].tolist(), df_right[COL_AGE].tolist(), "Age"), use_container_width=True, config=CHART_CONFIG)

with row1_r:
    st.plotly_chart(grouped_bar_fig("Initial Auth Duration", df_left[COL_INIT_AUTH].astype(str).tolist(), df_right[COL_INIT_AUTH].astype(str).tolist(), "Months / Status"), use_container_width=True, config=CHART_CONFIG)

with row2_l:
    st.plotly_chart(grouped_bar_fig("Reauth Duration", df_left[COL_REAUTH_DUR].astype(str).tolist(), df_right[COL_REAUTH_DUR].astype(str).tolist(), "Months / Status"), use_container_width=True, config=CHART_CONFIG)

with row2_r:
    all_step_x = sorted(set(df_left["steps_total_num"].tolist() + df_right["steps_total_num"].tolist()))
    fig_steps = go.Figure()
    for brand_name, dset, c_brand, c_gen in [
        (brand_left, df_left, NAVY, "#3A5A8C"),
        (brand_right, df_right, ORANGE, "#FAA85F"),
    ]:
        b_counts = dset["steps_brand_num"].value_counts().reindex(all_step_x, fill_value=0)
        g_counts = dset["steps_generic_num"].value_counts().reindex(all_step_x, fill_value=0)
        x_str = [str(v) for v in all_step_x]
        fig_steps.add_trace(go.Bar(name=f"{brand_name} — Brand", x=x_str, y=b_counts.values, marker_color=c_brand))
        fig_steps.add_trace(go.Bar(name=f"{brand_name} — Generic", x=x_str, y=g_counts.values, marker_color=c_gen))
    fig_steps.update_layout(barmode="stack", title="Step Count Distribution", xaxis_title="Total Steps",
                            yaxis_title="# Policies",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            **CHART_LAYOUT)
    st.plotly_chart(fig_steps, use_container_width=True, config=CHART_CONFIG)

# ── Gap Table ─────────────────────────────────────────────────────────────────
st.markdown(section_header("Restrictiveness Gap Analysis", "Most common value per parameter"), unsafe_allow_html=True)


def mode_val(series):
    vc = series.value_counts()
    return str(vc.index[0]) if len(vc) > 0 else "—"


params = [
    ("Age", df_left[COL_AGE], df_right[COL_AGE]),
    ("# Steps (typical)", df_left["steps_total_num"].astype(str), df_right["steps_total_num"].astype(str)),
    ("TB Test", df_left[COL_TB], df_right[COL_TB]),
    ("Quantity Limits", df_left["has_ql"].map({True: "Yes", False: "No"}), df_right["has_ql"].map({True: "Yes", False: "No"})),
    ("Specialist", df_left[COL_SPECIALIST], df_right[COL_SPECIALIST]),
    ("Init Auth (months)", df_left[COL_INIT_AUTH], df_right[COL_INIT_AUTH]),
    ("Reauth Duration (months)", df_left[COL_REAUTH_DUR], df_right[COL_REAUTH_DUR]),
]

rows_html = ""
for param, l_s, r_s in params:
    lv = mode_val(l_s)
    rv = mode_val(r_s)
    match = lv == rv
    row_bg = "#F0FDF4" if match else "#FFFBEB"
    icon = "✅" if match else "⚠️"
    gap_color = "#2E7D32" if match else "#E65100"
    rows_html += f"""<tr style="background:{row_bg}">
  <td style="padding:11px 16px;font-weight:600;color:#1B365D;border-bottom:1px solid #F3F4F6">{param}</td>
  <td style="padding:11px 16px;text-align:center;color:#1B365D;border-bottom:1px solid #F3F4F6">{lv}</td>
  <td style="padding:11px 16px;text-align:center;color:#F37021;border-bottom:1px solid #F3F4F6">{rv}</td>
  <td style="padding:11px 16px;text-align:center;font-size:16px;color:{gap_color};border-bottom:1px solid #F3F4F6">{icon}</td>
</tr>"""

gap_html = f"""
<table style="width:100%;border-collapse:collapse;border-radius:12px;
              overflow:hidden;box-shadow:0 2px 12px rgba(27,54,93,0.10)">
  <thead>
    <tr style="background:#1B365D;color:white">
      <th style="padding:13px 16px;text-align:left;font-weight:600;font-size:13px">Parameter</th>
      <th style="padding:13px 16px;text-align:center;font-weight:600;font-size:13px">{brand_left}</th>
      <th style="padding:13px 16px;text-align:center;font-weight:600;font-size:13px">{brand_right}</th>
      <th style="padding:13px 16px;text-align:center;font-weight:600;font-size:13px">Match</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>"""

st.markdown(gap_html, unsafe_allow_html=True)

# ── Summary Verdict ───────────────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

more_accessible = brand_left if avg_l >= avg_r else brand_right
less_accessible = brand_right if avg_l >= avg_r else brand_left
best_score = max(avg_l, avg_r)
worst_score = min(avg_l, avg_r)
diff_score = abs(avg_l - avg_r)

if diff_score < 2:
    s1 = (f"<b>{brand_left}</b> and <b>{brand_right}</b> have nearly identical average access scores "
          f"({avg_l} vs {avg_r}), suggesting comparable formulary positioning across payers.")
else:
    s1 = (f"<b>{more_accessible}</b> demonstrates better overall payer access with an average score of "
          f"<b>{best_score}</b> vs {worst_score} for <b>{less_accessible}</b>.")

more_restrict_step = brand_left if step_pct_l >= step_pct_r else brand_right
step_diff = abs(step_pct_l - step_pct_r)
if step_diff < 5:
    s2 = (f"Both brands face similar step therapy burden ({step_pct_l}% vs {step_pct_r}%), "
          f"with TB testing required by {'both brands equally' if abs(tb_l-tb_r)<5 else (brand_left if tb_l>tb_r else brand_right)}.")
else:
    s2 = (f"<b>{more_restrict_step}</b> faces heavier step therapy requirements "
          f"({max(step_pct_l, step_pct_r):.0f}% vs {min(step_pct_l, step_pct_r):.0f}%), "
          f"indicating greater restrictiveness pressure in its coverage policies.")

st.markdown(f"""
<div style="background:linear-gradient(135deg,#EEF2F8,#F5F7FA);border-radius:12px;
            padding:22px 26px;border-left:4px solid #F37021;margin-top:8px">
  <div style="font-size:12px;font-weight:700;color:#1B365D;text-transform:uppercase;
              letter-spacing:0.9px;margin-bottom:12px">📊 Summary Verdict</div>
  <p style="color:#374151;font-size:14px;margin:0 0 10px 0;line-height:1.7">{s1}</p>
  <p style="color:#374151;font-size:14px;margin:0;line-height:1.7">{s2}</p>
</div>
""", unsafe_allow_html=True)
