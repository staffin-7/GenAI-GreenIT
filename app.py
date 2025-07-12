
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from backend import CarbonBackend
import pydeck as pdk
from component import render_sustainability_score



backend = CarbonBackend()

st.set_page_config(
    page_title="CarbonWise 🌍 | Sustainable IT Dashboard",
    layout="wide",
    page_icon="🌱"
)

st.sidebar.title("📁 Upload")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type="csv")

if uploaded_file:
    backend.load_data(uploaded_file)
    st.sidebar.success("✅ Data loaded!")

    with st.sidebar.expander("⚙️ Settings", expanded=False):

        # -------- THRESHOLDS --------
        st.markdown("### 🧪 Thresholds")
        backend.co2_threshold = st.slider("CO₂ Threshold (kg)", 0.1, 5.0, 1.0, 0.1)
        backend.cpu_threshold = st.slider("CPU Utilization (%)", 10, 100, 80, 5)

        st.divider()

        # -------- SUSTAINABILITY SCORE CRITERIA --------
        st.markdown("### 🌿 Sustainability Score Criteria")
        co2_eff_cutoff = st.number_input("CO₂ Efficiency (kg/kWh)", min_value=0.01, max_value=1.0, value=0.05, step=0.01)
        cpu_avg_cutoff = st.number_input("CPU Avg Util (%)", min_value=10, max_value=100, value=85, step=1)
        pue_cutoff = st.number_input("PUE", min_value=1.0, max_value=5.0, value=1.6, step=0.1)
        ci_cutoff = st.number_input("Carbon Intensity (gCO₂/kWh)", min_value=50, max_value=1000, value=200, step=10)

        st.divider()

        # -------- FILTERS --------
        st.markdown("### 📅 Date & Location Filters")
        all_dates = backend.df['Date'].dt.date.unique()
        min_date, max_date = min(all_dates), max(all_dates)

        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        selected_locations = st.multiselect(
            "🌐 Data Center Location(s)",
            options=backend.df['Data_Center_Location'].unique(),
            default=list(backend.df['Data_Center_Location'].unique())
        )

    # DATA FILTERING & SCORE LOGIC
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = backend.get_filtered_data(start_date, end_date, selected_locations)
    else:
        filtered_data = backend.df.copy()

    if filtered_data.empty:
        st.warning("🚫 No data available for the selected date or date range.")
    else:
        summary = backend.get_summary_stats(filtered_data)
        co2_efficiency = summary['total_co2'] / summary['total_energy'] if summary['total_energy'] else 0

        sustainability_score = sum([
            co2_efficiency < co2_eff_cutoff,
            summary['avg_cpu'] < cpu_avg_cutoff,
            backend.df['PUE'].mean() < pue_cutoff,
            backend.df['Carbon_Intensity_gCO2/kWh'].mean() < ci_cutoff
        ])



        st.title("🌿 SustainIQ: Sustainable IT Dashboard")
        render_sustainability_score(sustainability_score)
        st.markdown("> Monitor and optimize your IT infrastructure's environmental impact.")
        mean_ci = backend.df['Carbon_Intensity_gCO2/kWh'].mean()

        k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
        k1.metric("Total CO₂ Emissions", f"{summary['total_co2']:.2f} kg")
        k2.metric("Avg CPU Utilization", f"{summary['avg_cpu']:.1f}%")
        k3.metric("Total Energy Used", f"{summary['total_energy']:.1f} kWh")
        breached_servers = filtered_data[filtered_data['Threshold_Breach'] == 'Yes']['Server_ID'].nunique()
        k4.metric("⚠️ Breached Servers", f"{breached_servers}")
        k5.metric("CO₂ Efficiency", f"{co2_efficiency:.2f} kg/kWh")
        k6.metric("Avg PUE", f"{backend.df['PUE'].mean():.2f}")
        k7.metric("Shift Workloads", f"{mean_ci:.0f} g/kWh")

        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🚨 Alerts", "🌍 Sustainability"])

        with tab1:
            server_emissions = (
            filtered_data.groupby("Server_ID", as_index=False)["Total_CO2_kg"]
            .sum()
            .sort_values("Total_CO2_kg", ascending=False)
        )

            server_chart = alt.Chart(server_emissions).mark_bar().encode(
                x=alt.X("Server_ID:N", sort='-y', title="Server ID"),
                y=alt.Y("Total_CO2_kg:Q", title="Total CO₂ Emissions (kg)"),
                color=alt.Color("Total_CO2_kg:Q", scale=alt.Scale(scheme="reds")),
                tooltip=["Server_ID", "Total_CO2_kg"]
            ).properties(
                title="🔝 Total CO₂ Emissions by Server",
                height=300
            ).configure_axis(grid=False)

            st.altair_chart(server_chart, use_container_width=True)

            filtered_data["Hour"] = pd.to_datetime(filtered_data["DateTime"]).dt.hour

            hourly_avg = (
                filtered_data.groupby("Hour", as_index=False)["Total_CO2_kg"]
                .mean()
                .sort_values("Total_CO2_kg", ascending=False)
            )

            hour_chart = alt.Chart(hourly_avg).mark_bar().encode(
            x=alt.X("Hour:O", title="Hour of Day", sort=alt.SortOrder("ascending")),  # maintain natural order
            y=alt.Y("Total_CO2_kg:Q", title="Avg CO₂ Emissions (kg)"),
            color=alt.Color("Total_CO2_kg:Q", scale=alt.Scale(scheme="greens"), legend=None),
            tooltip=["Hour", "Total_CO2_kg"]
        ).properties(
            title="⏱️ Hourly Avg CO₂ Emissions (0–23)",
            height=300
        ).configure_axis(grid=False)

            st.altair_chart(hour_chart, use_container_width=True)



        with tab2:
            st.subheader("📉 Daily Emission Trend by Server")
            top_emitters = (
                filtered_data.groupby('Server_ID')['Total_CO2_kg']
                .sum()
                .sort_values(ascending=False)
                .head(5).index.tolist()
            )
            selected_servers = st.multiselect(
                "Select Servers to Display",
                options=filtered_data['Server_ID'].unique().tolist(),
                default=top_emitters
            )
            if selected_servers:
                trend_data = filtered_data[filtered_data['Server_ID'].isin(selected_servers)]
                trend_chart = alt.Chart(trend_data).mark_line(point=True).encode(
                    x='Date:T',
                    y='Total_CO2_kg:Q',
                    color='Server_ID:N',
                    tooltip=['Date:T', 'Server_ID', 'Total_CO2_kg']
                ).properties(height=400)
                st.altair_chart(trend_chart, use_container_width=True)
            else:
                st.info("Select at least one server to view emission trends.")
            # Create a 2-column layout
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🌡️ Temperature vs Emissions")
                scatter = alt.Chart(filtered_data).mark_circle(size=60, opacity=0.8).encode(
                    x=alt.X('Temperature_Celsius:Q', title='Temperature (°C)', scale=alt.Scale(zero=False)),
                    y=alt.Y('Total_CO2_kg:Q', title='CO₂ Emissions (kg)'),
                    color='Data_Center_Location:N',
                    tooltip=['Server_ID', 'Temperature_Celsius', 'Total_CO2_kg']
                ).properties(
                    height=350,
                    title="🌡️ Temperature vs Emissions"
                )

                st.altair_chart(scatter, use_container_width=True)

            with col2:
                st.markdown("### ⚡ Energy vs CO₂ Emissions")
                scatter_energy = alt.Chart(filtered_data).mark_circle(size=60).encode(
                    x='Energy_Consumption_kWh:Q',
                    y='Total_CO2_kg:Q',
                    color='Data_Center_Location:N',
                    tooltip=['Server_ID', 'Energy_Consumption_kWh', 'Total_CO2_kg']
                ).properties(height=350)
                st.altair_chart(scatter_energy, use_container_width=True)

        with tab3:
            st.subheader("🚨 Threshold Breaches")

            # Filter only breached rows using existing column
            breach_df = filtered_data[filtered_data['Threshold_Breach'] == 'Yes']

            if breach_df.empty:
                st.success("✅ No breaches detected!")
            else:
                # 📊 Breach count by server
                breach_counts = (
                    breach_df.groupby("Server_ID")
                    .size()
                    .reset_index(name="Breach_Count")
                    .sort_values("Breach_Count", ascending=False)
                )

                breach_chart = alt.Chart(breach_counts).mark_bar().encode(
                    x=alt.X("Server_ID:N", sort='-y', title="Server"),
                    y=alt.Y("Breach_Count:Q", title="Breach Count"),
                    color=alt.Color("Breach_Count:Q", scale=alt.Scale(scheme="oranges")),
                    tooltip=["Server_ID", "Breach_Count"]
                ).properties(
                    title="📊 CO₂ Threshold Breaches by Server",
                    height=300
                )

                st.altair_chart(breach_chart, use_container_width=True)

                # 🔍 Breach Highlights
                most_breached = breach_counts.iloc[0]
                worst_breach = breach_df.loc[breach_df["Total_CO2_kg"].idxmax()]

                st.markdown("### 🔎 Breach Highlights")
                st.markdown(f"- **Most Breached Server**: `{most_breached['Server_ID']}` with **{most_breached['Breach_Count']}** breaches")
                st.markdown(f"- **Highest Single Breach**: `{worst_breach['Server_ID']}` with **{worst_breach['Total_CO2_kg']:.2f} kg CO₂** on `{worst_breach['DateTime']}`")

                # 🧾 Expandable breach detail table
                with st.expander("📋 Show Detailed Breach List"):
                    st.dataframe(
                        breach_df[["Server_ID", "DateTime", "Total_CO2_kg", "Data_Center_Location", "CPU_Utilisation (%)", "Energy_Consumption_kWh"]]
                        .sort_values("Total_CO2_kg", ascending=False)
                        .reset_index(drop=True),
                        use_container_width=True
            )


        with tab4:
            st.subheader("🗺️ Carbon Intensity & Efficiency Insights (Map View)")
            # Prepare map data
            map_data = filtered_data.groupby(["Data_Center_Location", "Latitude", "Longitude"]).agg(
                Total_CO2_kg=("Total_CO2_kg", "sum"),
                Carbon_Intensity=("Carbon_Intensity_gCO2/kWh", "mean"),
                PUE=("PUE", "mean"),
                Servers=("Server_ID", "nunique")
            ).reset_index()

            # Create Pydeck layer
            layer = pdk.Layer(
                "ColumnLayer",
                data=map_data,
                get_position='[Longitude, Latitude]',
                get_elevation='Total_CO2_kg * 100',
                elevation_scale=1,
                radius=20000,
                get_fill_color='[255, 255 - Carbon_Intensity, 100]',
                pickable=True,
                auto_highlight=True,
            )

            # Define camera view
            view_state = pdk.ViewState(
                latitude=map_data["Latitude"].mean(),
                longitude=map_data["Longitude"].mean(),
                zoom=3,
                pitch=45,
            )

            # Render in Streamlit
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={
                    "html": "<b>{Data_Center_Location}</b><br/>"
                            "CO₂: {Total_CO2_kg} kg<br/>"
                            "Intensity: {Carbon_Intensity} g/kWh<br/>"
                            "PUE: {PUE}<br/>"
                            "Servers: {Servers}",
                    "style": {"backgroundColor": "black", "color": "white"}
                },
                map_style="mapbox://styles/mapbox/light-v9"
            ))

            st.markdown("### ✅ Sustainability Recommendations")
            if co2_efficiency > 0.1:
                st.write("- Optimize high CO₂ servers or consolidate workloads")
            if backend.df['PUE'].mean() > 1.7:
                st.write("- Upgrade data center cooling or airflow systems")
            if backend.df['Carbon_Intensity_gCO2/kWh'].mean() > 300:
                st.write("- Shift workloads to regions like Norway")
            if summary['avg_cpu'] > 90:
                st.write("- Distribute CPU load or use autoscaling")
            # Extract live values
            avg_cpu = summary['avg_cpu']
            mean_pue = backend.df['PUE'].mean()
            mean_ci = backend.df['Carbon_Intensity_gCO2/kWh'].mean()

            # Smart Recommendations to reach 4/4
            st.markdown("### 🧠 How to Reach a Sustainability Score of 4/4")

            unmet_criteria = []

            if co2_efficiency >= co2_eff_cutoff:
                unmet_criteria.append(f"- Reduce CO₂ emissions per kWh below **{co2_eff_cutoff}** (currently {co2_efficiency:.2f})")

            if avg_cpu >= cpu_avg_cutoff:
                unmet_criteria.append(f"- Optimize CPU usage to stay below **{cpu_avg_cutoff}%** (currently {avg_cpu:.1f}%)")

            if mean_pue >= pue_cutoff:
                unmet_criteria.append(f"- Improve infrastructure to reduce PUE below **{pue_cutoff}** (currently {mean_pue:.2f})")

            if mean_ci >= ci_cutoff:
                unmet_criteria.append(f"- Shift workloads to greener regions (target CI < **{ci_cutoff}**, currently {mean_ci:.0f})")

            if unmet_criteria:
                for tip in unmet_criteria:
                    st.write(tip)
            else:
                st.success("🎉 You're already meeting all criteria for a score of 4/4!")

            st.caption("_🧠 More personalized suggestions will be powered by GenAI soon..._")

        st.markdown("---")
        st.markdown("Built for UCD x Deloitte | Capstone 2025 🌱")

else:
    st.warning("Please upload a CSV file to begin.")
