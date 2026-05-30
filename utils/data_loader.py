import pandas as pd
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "result_cleaned.csv"

COL_FILENAME = "Filename"
COL_BRAND = "Brand"
COL_AGE = "Age"
COL_STEP_TEXT = "Step Therapy Requirements Documented in Policy"
COL_STEPS_BRAND = "Number of Steps through Brands"
COL_STEPS_GENERIC = "Number of Steps through Generic"
COL_PHOTOTHERAPY = "Step through-Phototherapy"
COL_TB = "TB Test required"
COL_QL = "Quantity Limits"
COL_SPECIALIST = "Specialist Types"
COL_INIT_AUTH = "Initial Authorization Duration(in-months)"
COL_REAUTH_DUR = "Reauthorization Duration(in-months)"
COL_REAUTH_REQ = "Reauthorization Required"
COL_REAUTH_TEXT = "Reauthorization Requirements Documented in Policy"
COL_ACCESS = "Access Score"

ALL_COLUMNS = [
    COL_FILENAME, COL_BRAND, COL_AGE, COL_STEP_TEXT,
    COL_STEPS_BRAND, COL_STEPS_GENERIC, COL_PHOTOTHERAPY,
    COL_TB, COL_QL, COL_SPECIALIST, COL_INIT_AUTH,
    COL_REAUTH_DUR, COL_REAUTH_REQ, COL_REAUTH_TEXT, COL_ACCESS,
]


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load result_cleaned.csv with proper NA handling and add derived numeric columns."""
    if not DATA_PATH.exists():
        st.error(f"Data file not found: {DATA_PATH}. Place result_cleaned.csv in dashboard/data/.")
        st.stop()

    df = pd.read_csv(DATA_PATH, keep_default_na=False)

    missing = [c for c in ALL_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"CSV is missing expected columns: {missing}")
        st.stop()

    def parse_step_count(v: str) -> int:
        v = str(v).strip()
        if v in ("No", "", "NA"):
            return 0
        try:
            return int(v)
        except ValueError:
            return 0

    def parse_duration(v: str):
        v = str(v).strip()
        if v in ("Unspecified", "NA", "No", ""):
            return None
        try:
            return int(v)
        except ValueError:
            return None

    df["steps_brand_num"] = df[COL_STEPS_BRAND].apply(parse_step_count)
    df["steps_generic_num"] = df[COL_STEPS_GENERIC].apply(parse_step_count)
    df["steps_total_num"] = df["steps_brand_num"] + df["steps_generic_num"]
    df["init_auth_num"] = df[COL_INIT_AUTH].apply(parse_duration)
    df["reauth_dur_num"] = df[COL_REAUTH_DUR].apply(parse_duration)
    df["has_step_therapy"] = df["steps_total_num"] > 0
    df["has_ql"] = ~df[COL_QL].isin(["No", "NA", ""])

    return df
