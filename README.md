# Payer PA Policy Intelligence — Dashboard

A 3-page Streamlit dashboard exploring 79 US payer Prior Authorization policies for Plaque Psoriasis.

## Pages

1. **Landscape** — KPIs, Access Score distribution, brand-level restrictiveness
2. **Policy Drilldown** — search, filter, inspect any policy
3. **Brand Comparison** — side-by-side TREMFYA vs STELARA (or any 2 brands)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in a browser.

## Data

`data/result_cleaned.csv` — 79 rows × 15 columns. Output of the upstream GenAI pipeline (`pa_pipeline.py`, separate deliverable).

## Deploy

Push to a public GitHub repo, then deploy from [streamlit.io/cloud](https://streamlit.io/cloud). Point at `app.py` as the entry file.

## Branding

Uses ZS Associates colors (navy `#1B365D`, orange `#F37021`) and Calibri font.
