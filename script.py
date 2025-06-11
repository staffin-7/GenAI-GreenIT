import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Load data (replace with your actual CSV)
df = pd.read_csv("/Users/arunsoorya/Documents/Semester_3/Capstone/Code/Simulated_Carbon-Aware_Server_Dataset.csv")

# Streamlit page settings
st.set_page_config(page_title="Green IT Dashboard", layout="wide")

# --- HEADER ---
st.markdown("""
    <style>
        .main {background-color: #f5f7fa;}
        h1 {color: #2a9d8f; font-size: 36px;}
        .metric-label {font-weight: 600; color: #264653;}
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🌿 Green IT: Carbon-Aware Server Dashboard")

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filters")
selected_date = st.sidebar.selectbox("Select Date", sorted(df["Date"].unique()))
selected_location = st.sidebar.multiselect(
    "Select Data Center(s)", df["Data_Center_Location"].unique(), default=df["Data_Center_Location"].unique()
)

# --- FILTER DATA ---
data = df[(df["Date"] == selected_date) & (df["Data_Center_Location"].isin(selected_location))]

# --- KPI CARDS ---
st.markdown("### 📊 Daily Summary")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="🌍 Total CO₂ Emissions (kg)", value=f"{data['Total_CO2_kg'].sum():.2f}")
kpi2.metric(label="🖥️ Avg. CPU Utilisation (%)", value=f"{data['CPU_Utilisation (%)'].mean():.1f}")
kpi3.metric(label="⚡ Avg. Energy Use (kWh)", value=f"{data['Energy_Consumption_kWh'].mean():.2f}")
kpi4.metric(label="🚨 Breaches Today", value=data[data['Threshold_Breach'] == 'Yes'].shape[0])

# --- EMISSIONS CHART ---
st.markdown("### 📈 Emissions by Server")
bar_chart = alt.Chart(data).mark_bar().encode(
    x=alt.X("Server_ID:N", title="Server"),
    y=alt.Y("Total_CO2_kg:Q", title="CO₂ Emissions (kg)"),
    color=alt.condition(
        alt.datum.Threshold_Breach == 'Yes', alt.value("#e76f51"), alt.value("#2a9d8f")
    ),
    tooltip=["Server_ID", "Total_CO2_kg", "Energy_Consumption_kWh", "CPU_Utilisation (%)"]
).properties(width=850, height=400)

st.altair_chart(bar_chart, use_container_width=True)

# --- DATA TABLE ---
st.markdown("### 🧾 Detailed Server Metrics")
with st.expander("View Full Table"):
    st.dataframe(data.sort_values(by="Total_CO2_kg", a
    ending=False).reset_index(drop=True), use_container_width=True)

# --- GPT RECOMMENDATIONS ---
st.markdown("### 🤖 GenAI-Based Recommendations")

breach_servers = data[data['Threshold_Breach'] == 'Yes']

if not breach_servers.empty:
    for index, row in breach_servers.iterrows():
        st.warning(f"**Server {row['Server_ID']}** in **{row['Data_Center_Location']}** exceeded the CO₂ limit with **{row['Total_CO2_kg']} kg**.\n\n💡 _Recommendation:_ Consider scaling down workloads during off-peak hours or migrating to a lower-carbon region.")
else:
    st.success("✅ No breaches today. All servers are operating within acceptable carbon limits.")
