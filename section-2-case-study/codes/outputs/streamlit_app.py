
import streamlit as st
import pandas as pd

st.set_page_config(page_title="ECDA Preschool Planning Tool", layout="wide")

gap = pd.read_csv("priority_ranking_base_preschool.csv")
metrics = pd.read_csv("model_backtest_metrics.csv")
scenario_summary = pd.read_csv("scenario_summary.csv")

st.title("ECDA Preschool Demand Forecasting Tool")

st.subheader("Model Backtesting Performance")
st.dataframe(metrics, use_container_width=True)

year = st.selectbox("Forecast year", sorted(gap["year"].unique()))
top_n = st.slider("Show top N priority subzones", 10, 100, 30)

df = gap[gap["year"] == year].sort_values("priority_rank").head(top_n)

col1, col2, col3 = st.columns(3)
col1.metric("Forecast demand", int(df["forecast_demand_children"].sum()))
col2.metric("Shortfall children", int(df["shortfall_children"].sum()))
col3.metric("Additional centres needed", int(df["additional_centres_needed"].sum()))

st.subheader("Priority Ranking")
st.dataframe(df, use_container_width=True)

st.subheader("Supply Scenario Sensitivity")
st.dataframe(scenario_summary[scenario_summary["year"] == year], use_container_width=True)

st.subheader("Additional Centres Needed")
st.bar_chart(df.set_index("subzone_clean")["additional_centres_needed"])

st.download_button(
    label="Download priority table",
    data=df.to_csv(index=False),
    file_name=f"priority_subzones_{year}.csv",
    mime="text/csv"
)
