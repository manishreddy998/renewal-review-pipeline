"""Renewal review dashboard. Reads the CSV files in results/."""
from pathlib import Path

import pandas as pd
import streamlit as st

RESULTS = Path(__file__).resolve().parent.parent / "results"
AGENCIES = {
    "AGY001": "Maple Lane Insurance Brokers (fictional)",
    "AGY002": "Lakeshore Risk Partners (fictional)",
    "AGY003": "Northbay Family Insurance (fictional)",
}

st.set_page_config(page_title="Renewal Review", layout="wide")
st.caption("SYNTHETIC TEST DATA, NOT A REAL POLICY")
st.title("Renewal Review")

queue = pd.read_csv(RESULTS / "renewal_queue.csv")
evidence = pd.read_csv(RESULTS / "change_evidence.csv")
accuracy = pd.read_csv(RESULTS / "field_accuracy.csv")
detection = pd.read_csv(RESULTS / "change_detection.csv")
cost = pd.read_csv(RESULTS / "cost.csv")

agency = st.sidebar.selectbox("Agency", list(AGENCIES), format_func=lambda a: AGENCIES[a])
st.sidebar.write("Each agency only sees its own accounts.")
q = queue[queue.agency_id == agency]

overall = accuracy[accuracy.field.isna()].accuracy.iloc[0]
alldet = detection[detection.change_type == "all changes"].iloc[0]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Renewals", len(q))
c2.metric("Review now", int((q.priority == "review now").sum()))
c3.metric("Field accuracy", f"{overall:.1%}")
c4.metric("Change recall", f"{alldet.recall:.1%}")
c5.metric("Cost per document", f"${cost.usd_per_document.iloc[0]:.4f}")

st.subheader("Work list")
show = q[["agency_rank", "priority", "risk_score", "policy_number", "insured_name",
          "prior_premium", "renewal_premium", "premium_change_pct", "reasons", "needs_data_check"]]
st.dataframe(show, hide_index=True, use_container_width=True, height=360)

st.subheader("Why is this account flagged?")
pick = st.selectbox("Policy", q.policy_number.tolist())
pair_id = q[q.policy_number == pick].pair_id.iloc[0]
ev = evidence[evidence.pair_id == pair_id][[
    "change_type", "prior_value", "prior_page", "prior_evidence",
    "renewal_value", "renewal_page", "renewal_evidence"]]
if ev.empty:
    st.write("No changes flagged for this account.")
else:
    st.dataframe(ev, hide_index=True, use_container_width=True)
