"""
Project FORESIGHT - AI-Powered Demand & Inventory Intelligence Dashboard
Run with: streamlit run app.py

Zaroori files (isi folder mein rakhein):
- foresight_risk_output.csv
- sales_history.csv
- forecast_results.csv
- future_demand_forecast.csv
- .streamlit/config.toml   (theme colors ke liye)
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="FORESIGHT | Inventory Intelligence", layout="wide", page_icon="📦")

# ---------- Custom CSS ----------
st.markdown("""
<style>
    [data-testid="stMainMenu"] { display: none !important; }
    [data-testid="stAppDeployButton"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    .main { padding-top: 1rem; }

    /* KPI card look */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"] { font-weight: 600; color: #64748B; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #0F172A; }

    /* Header banner */
    .foresight-header {
        background: linear-gradient(90deg, #2563EB 0%, #1E40AF 100%);
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 20px;
    }
    .foresight-header h1 { color: white; margin: 0; font-size: 1.9rem; }
    .foresight-header p { color: #DBEAFE; margin: 4px 0 0 0; font-size: 0.95rem; }

    /* Section subheaders */
    h3 { color: #1E293B; border-left: 4px solid #2563EB; padding-left: 10px; }

    /* Tabs */
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; }

    /* Dataframe container */
    div[data-testid="stDataFrame"] { border: 1px solid #E2E8F0; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ---------- Consistent Color Palette ----------
RISK_COLORS = {"Stockout Risk": "#DC2626", "Overstock Risk": "#F59E0B", "Healthy": "#16A34A"}
CHART_BLUE = "#2563EB"
CHART_GRAY = "#94A3B8"
CHART_ORANGE = "#EA580C"

plt.rcParams.update({
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": "#334155",
    "xtick.color": "#334155",
    "ytick.color": "#334155",
    "axes.titleweight": "bold",
    "axes.titlecolor": "#1E293B",
    "font.size": 10,
})

# ---------- Data Load ----------
@st.cache_data
def load_data():
    risk = pd.read_csv("foresight_risk_output.csv")
    history = pd.read_csv("sales_history.csv", parse_dates=["Date"])
    forecast = pd.read_csv("forecast_results.csv", parse_dates=["Date"])
    future = pd.read_csv("future_demand_forecast.csv", parse_dates=["Date"])
    return risk, history, forecast, future

risk_df, history_df, forecast_df, future_df = load_data()

# ---------- Header ----------
st.markdown("""
<div class="foresight-header">
    <h1>📦 Project FORESIGHT</h1>
    <p>AI-Powered Demand Forecasting &amp; Inventory Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ---------- KPI Cards ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total SKUs", len(risk_df))
col2.metric("🔴 Stockout Risk", int((risk_df["Risk_Status"] == "Stockout Risk").sum()))
col3.metric("🟠 Overstock Risk", int((risk_df["Risk_Status"] == "Overstock Risk").sum()))
col4.metric("🟢 Healthy SKUs", int((risk_df["Risk_Status"] == "Healthy").sum()))

st.write("")

# ---------- Tabs ----------
tab1, tab2 = st.tabs(["📊  Current Analysis", "🔮  Future Forecast (Next 30 Days)"])

# ==================== TAB 1: CURRENT ANALYSIS ====================
with tab1:
    st.sidebar.header("🔍 Filters")
    categories = ["All"] + sorted(risk_df["Category"].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)

    risk_options = ["All"] + sorted(risk_df["Risk_Status"].unique().tolist())
    selected_risk = st.sidebar.selectbox("Risk Status", risk_options)

    filtered = risk_df.copy()
    if selected_category != "All":
        filtered = filtered[filtered["Category"] == selected_category]
    if selected_risk != "All":
        filtered = filtered[filtered["Risk_Status"] == selected_risk]

    left, right = st.columns([1, 2])

    with left:
        st.markdown("### Risk Distribution")
        risk_counts = risk_df["Risk_Status"].value_counts()
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        ax1.bar(risk_counts.index, risk_counts.values,
                color=[RISK_COLORS.get(x, "#94A3B8") for x in risk_counts.index],
                width=0.55)
        ax1.set_ylabel("Number of SKUs")
        ax1.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig1)

    with right:
        st.markdown("### SKU-Wise Inventory Risk Table")
        st.dataframe(
            filtered[["SKU", "Product_Name", "Category", "Current_Stock",
                      "avg_daily_demand", "days_of_stock", "Lead_Time_Days",
                      "Reorder_Point", "Risk_Status"]]
            .sort_values("days_of_stock"),
            use_container_width=True,
            height=350,
        )

    st.divider()

    st.markdown("### 🔎 SKU Deep-Dive: Demand Forecast Accuracy")

    sku_list = sorted(risk_df["SKU"].unique().tolist())
    selected_sku = st.selectbox("SKU Chuno", sku_list, key="tab1_sku")

    sku_history = history_df[history_df["SKU"] == selected_sku]
    sku_forecast = forecast_df[forecast_df["SKU"] == selected_sku]
    sku_risk = risk_df[risk_df["SKU"] == selected_sku].iloc[0]

    info_col1, info_col2, info_col3 = st.columns(3)
    info_col1.metric("Current Stock", int(sku_risk["Current_Stock"]))
    info_col2.metric("Avg Daily Demand", f"{sku_risk['avg_daily_demand']:.1f}")
    info_col3.metric("Risk Status", sku_risk["Risk_Status"])

    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(sku_history["Date"], sku_history["Units_Sold"], label="Historical Sales",
             color=CHART_GRAY, alpha=0.6)
    ax2.plot(sku_forecast["Date"], sku_forecast["Actual"], label="Actual (Test Period)",
             color=CHART_BLUE, marker="o", markersize=3)
    ax2.plot(sku_forecast["Date"], sku_forecast["Predicted"], label="Predicted (Test Period)",
             color=CHART_ORANGE, marker="x", markersize=3)
    ax2.set_title(f"Demand History & Forecast Accuracy — {selected_sku}")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.legend(frameon=False)
    st.pyplot(fig2)

    st.divider()

    st.markdown("### 🔔 Reorder Recommendations")

    stockout_skus = risk_df[risk_df["Risk_Status"] == "Stockout Risk"].sort_values("days_of_stock")
    if len(stockout_skus) > 0:
        st.warning(f"⚠️ {len(stockout_skus)} SKUs ko turant reorder karna chahiye:")
        st.dataframe(
            stockout_skus[["SKU", "Product_Name", "Current_Stock", "days_of_stock", "Reorder_Point"]],
            use_container_width=True,
        )
    else:
        st.success("✅ Koi SKU stockout risk mein nahi hai.")

# ==================== TAB 2: FUTURE FORECAST ====================
with tab2:
    st.markdown("### 📅 Agle 30 Dinon Ka Demand Forecast")
    st.caption("Yeh naya forecast hai — jo abhi tak hua hi nahi, model ne predict kiya hai.")

    fc_categories = ["All"] + sorted(future_df["Category"].dropna().unique().tolist())
    selected_fc_category = st.selectbox("Category", fc_categories, key="tab2_category")

    future_filtered = future_df.copy()
    if selected_fc_category != "All":
        future_filtered = future_filtered[future_filtered["Category"] == selected_fc_category]

    total_by_sku = (
        future_filtered.groupby(["SKU", "Product_Name"])["Predicted_Demand"]
        .sum()
        .reset_index()
        .sort_values("Predicted_Demand", ascending=False)
    )

    top_col, chart_col = st.columns([1, 2])

    with top_col:
        st.markdown("**🏆 Top 10 SKUs by Predicted 30-Day Demand**")
        st.dataframe(total_by_sku.head(10), use_container_width=True, height=350)

    with chart_col:
        st.markdown("**📊 Predicted Demand by Category (Next 30 Days)**")
        cat_totals = future_filtered.groupby("Category")["Predicted_Demand"].sum().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.bar(cat_totals.index, cat_totals.values, color=CHART_BLUE, width=0.55)
        ax3.set_ylabel("Total Predicted Units")
        ax3.spines[["top", "right"]].set_visible(False)
        plt.xticks(rotation=30)
        st.pyplot(fig3)

    st.divider()

    st.markdown("### 📈 SKU-Wise Future Forecast Graph")
    future_sku_list = sorted(future_df["SKU"].unique().tolist())
    selected_future_sku = st.selectbox("SKU Chuno", future_sku_list, key="tab2_sku")

    sku_future = future_df[future_df["SKU"] == selected_future_sku].sort_values("Date")
    sku_past = history_df[history_df["SKU"] == selected_future_sku].sort_values("Date").tail(60)

    fig4, ax4 = plt.subplots(figsize=(12, 4))
    ax4.plot(sku_past["Date"], sku_past["Units_Sold"], label="Last 60 Days (Actual)",
             color=CHART_GRAY, alpha=0.7)
    ax4.plot(sku_future["Date"], sku_future["Predicted_Demand"], label="Next 30 Days (Forecast)",
             color=CHART_ORANGE, marker="o", markersize=3)
    ax4.axvline(sku_past["Date"].max(), color="#0F172A", linestyle="--", alpha=0.4, label="Today")
    ax4.set_title(f"Demand Forecast — {selected_future_sku}")
    ax4.spines[["top", "right"]].set_visible(False)
    ax4.legend(frameon=False)
    plt.xticks(rotation=45)
    st.pyplot(fig4)

    st.divider()

    st.markdown("### 📦 Reorder Planning Suggestion (Based on Future Demand)")
    reorder_plan = future_filtered.groupby(["SKU", "Product_Name"])["Predicted_Demand"].sum().reset_index()
    reorder_plan = reorder_plan.merge(
        risk_df[["SKU", "Current_Stock", "Reorder_Point"]], on="SKU", how="left"
    )
    reorder_plan["Shortfall_Next_30_Days"] = reorder_plan["Predicted_Demand"] - reorder_plan["Current_Stock"]
    reorder_plan = reorder_plan[reorder_plan["Shortfall_Next_30_Days"] > 0].sort_values(
        "Shortfall_Next_30_Days", ascending=False
    )

    if len(reorder_plan) > 0:
        st.warning(f"⚠️ {len(reorder_plan)} SKUs mein agle 30 dinon ka demand current stock se zyada hai:")
        st.dataframe(
            reorder_plan[["SKU", "Product_Name", "Current_Stock", "Predicted_Demand", "Shortfall_Next_30_Days"]],
            use_container_width=True,
        )
    else:
        st.success("✅ Sab SKUs ka current stock agle 30 din ke demand ke liye kaafi hai.")
