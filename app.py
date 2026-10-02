import pandas as pd
import streamlit as st
from scoring import clean_data, score_data

st.set_page_config(page_title="Technology Debt Calculator", layout="wide")
st.title("Technology Debt Score and ROI Calculator")
st.caption("A simplified demo model to prioritize legacy applications for retirement or migration.")

# ---- Inputs ----
uploaded = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
horizon = st.slider("Savings horizon (years)", min_value=1, max_value=10, value=3)

if uploaded is not None:
    if uploaded.name.endswith(".xlsx"):
        raw = pd.read_excel(uploaded)
    else:
        raw = pd.read_csv(uploaded)
else:
    st.info("No file uploaded, so the sample data is being used.")
    raw = pd.read_csv("sample_apps.csv")

# ---- Clean and score ----
try:
    clean, rejected = clean_data(raw)
except ValueError as error:
    st.error(str(error))
    st.stop()

result = score_data(clean, horizon_years=horizon)

# ---- Summary numbers ----
high = result[result["priority"] == "High"]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Applications analyzed", len(result))
col2.metric("High priority", len(high))
col3.metric("Net savings (High priority)", f"₹{high['net_savings'].sum():,.0f}")
col4.metric("Rows rejected", len(rejected))

# ---- Ranked table ----
st.subheader("Ranked applications")
st.dataframe(
    result[["app_name", "debt_score", "priority", "yearly_cost",
            "migration_cost", "net_savings", "roi_percent"]]
)

# ---- Charts ----
left, right = st.columns(2)
with left:
    st.subheader("Debt score by application")
    st.bar_chart(result.set_index("app_name")["debt_score"])
with right:
    st.subheader("Yearly cost by application")
    st.bar_chart(result.set_index("app_name")["yearly_cost"])

# ---- Rejected rows ----
st.subheader("Rejected rows (data quality report)")
if rejected.empty:
    st.success("No rows were rejected.")
else:
    st.dataframe(rejected[["app_name", "reject_reason"]])

# ---- Download ----
st.download_button(
    label="Download report (CSV)",
    data=result.to_csv(index=False).encode("utf-8"),
    file_name="tech_debt_report.csv",
    mime="text/csv",
)