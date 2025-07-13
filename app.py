
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from backend import CarbonBackend
import pydeck as pdk
from component import render_sustainability_score
from component import render_kpi_cards
import base64
from datetime import datetime
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


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



        st.title("🌿 CarbonWise: Sustainable IT Dashboard")
        render_sustainability_score(sustainability_score)
        st.markdown("> Monitor and optimize your IT infrastructure's environmental impact.")
        mean_ci = backend.df['Carbon_Intensity_gCO2/kWh'].mean()

        pue_avg = backend.df['PUE'].mean()
        render_kpi_cards(summary, co2_efficiency, pue_avg, mean_ci)

        st.markdown("---")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Trends", "🚨 Alerts", "🌍 Sustainability", "📄 Report"])


        with tab1:
            left_col, right_col = st.columns([2, 1])  # wider left side for charts

            with left_col:
                st.markdown("### 🔌 Energy vs CPU Efficiency")
                scatter = alt.Chart(filtered_data).mark_circle(size=60, opacity=0.6).encode(
                    x=alt.X('Energy_Consumption_kWh', title='Energy Used (kWh)', scale=alt.Scale(zero=False)),
                    y=alt.Y('CPU_Utilisation (%)', title='CPU Utilization (%)'),
                    color='Data_Center_Location',
                    tooltip=['Energy_Consumption_kWh', 'CPU_Utilisation (%)', 'Total_CO2_kg']
                ).properties(height=300)
                st.altair_chart(scatter, use_container_width=True)

                st.markdown("### ⏱️ Hourly CPU Utilization Trend")
                filtered_data["Hour"] = pd.to_datetime(filtered_data["DateTime"]).dt.hour
                hourly_cpu = filtered_data.groupby('Hour', as_index=False)['CPU_Utilisation (%)'].mean()
                cpu_chart = alt.Chart(hourly_cpu).mark_line(point=True).encode(
                    x=alt.X('Hour:O', title='Hour of Day'),
                    y=alt.Y('CPU_Utilisation (%)', title='Avg CPU Utilization (%)'),
                    tooltip=['Hour', 'CPU_Utilisation (%)']
                ).properties(height=300)
                st.altair_chart(cpu_chart, use_container_width=True)

            with right_col:
                st.markdown("### 🧠 GenAI Recommendations (Prototype)")
                st.info("These are preliminary suggestions based on observed patterns:")

                avg_cpu = filtered_data['CPU_Utilisation (%)'].mean()
                avg_pue = filtered_data['PUE'].mean()
                avg_energy = filtered_data['Energy_Consumption_kWh'].mean()
                server_days = filtered_data.groupby('Server_ID')['Date'].nunique()
                high_uptime_count = (server_days > 20).sum()  # arbitrary threshold, adjust as needed


                if avg_cpu < 50:
                    st.markdown("• 🚀 **Consolidate underutilized servers** — average CPU usage is low.")
                if avg_pue > 1.7:
                    st.markdown("• ❄️ **Improve cooling systems** — high average PUE detected.")
                if avg_energy > 1200:
                    st.markdown("• ⚡ **Reduce high energy usage** — workloads may be oversized.")
                if high_uptime_count > 30:
                    st.markdown("• 🔄 **Schedule maintenance** — several servers have extreme uptime.")

                st.caption("🧠 More personalized recommendations coming soon via GenAI.")



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
                map_style="mapbox://styles/mapbox/satellite-streets-v12"
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

        with tab5:    

            # --- Dynamic values (replace with your actual variables) ---
            locations = list(filtered_data['Data_Center_Location'].unique())
            pue = backend.df['PUE'].mean()
            co2_eff = co2_efficiency
            mean_ci = backend.df['Carbon_Intensity_gCO2/kWh'].mean()
            score = sustainability_score
            avg_cpu = summary['avg_cpu']

            recs = []
            if co2_eff >= 0.10:
                recs.append("🌍 Shift workloads to regions with lower carbon intensity.")
            if pue > 1.3:
                recs.append("❄️ Upgrade cooling infrastructure to lower PUE.")
            if co2_eff > 0.10:
                recs.append("🧪 Consolidate servers to reduce CO₂ per kWh.")
            if avg_cpu < 60:
                recs.append("⚡ Improve CPU utilization by decommissioning idle servers.")

            # --- Render in-tab visual report ---
            st.markdown("## 🌍 Sustainability Report Summary")
            st.markdown(f"**Date Generated:** {datetime.now():%Y-%m-%d %H:%M}")
            st.markdown(f"**Sustainability Score:** {score} / 4")
            st.markdown("---")

            st.markdown("### 📌 EU Carbon Emission Requirement")
            st.write("• EU recommends PUE < 1.3 and Carbon Intensity < 100 gCO₂/kWh by 2030.")

            st.markdown("### 📊 Uploaded Data Center Summary")
            st.write(f"• **Data Centers:** {len(locations)} ({', '.join(locations)})")
            st.write(f"• **Avg CO₂ Efficiency:** {co2_eff:.2f} kg/kWh")
            st.write(f"• **Avg PUE:** {pue:.2f}")
            st.write(f"• **Avg Carbon Intensity:** {mean_ci:.0f} g/kWh")
            st.write(f"• **Avg CPU Utilization:** {avg_cpu:.1f}%")

            st.markdown("### 🧠 AI Summary")
            st.write("While energy efficiency is decent, carbon intensity is above EU thresholds. Some servers are underutilized. Optimize workloads and infrastructure.")

            st.markdown("### 🏁 Recommendations")
            for r in recs:
                st.write(f"- {r}")

            st.markdown("---")

            # --- Build PDF ---
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=30)
            styles = getSampleStyleSheet()
            Story = []

            Story.append(Paragraph("<b><font size=16 color='#00cc99'>🌿 Sustainability Report Summary</font></b>", styles["Title"]))
            Story.append(Spacer(1, 12))
            Story.append(Paragraph(f"<font size=10><b>Date Generated:</b> {datetime.now():%Y-%m-%d %H:%M}</font>", styles["Normal"]))
            Story.append(Spacer(1, 6))
            Story.append(Paragraph(f"<font size=10><b>Sustainability Score:</b> {score} / 4</font>", styles["Normal"]))
            Story.append(Spacer(1, 16))

            Story.append(Paragraph("<b><font color='#ffaa00'>📌 EU Carbon Emission Requirement</font></b>", styles["Heading3"]))
            Story.append(Spacer(1, 4))
            Story.append(Paragraph("The EU recommends PUE < 1.3 and Carbon Intensity < 100 gCO₂/kWh by 2030.", styles["Normal"]))
            Story.append(Spacer(1, 12))

            Story.append(Paragraph("<b><font color='#33ccff'>📊 Uploaded Data Center Summary</font></b>", styles["Heading3"]))
            data_table = [
                ["Total Data Centers", f"{len(locations)} ({', '.join(locations)})"],
                ["Avg CO₂ Efficiency", f"{co2_eff:.2f} kg/kWh"],
                ["Avg PUE", f"{pue:.2f}"],
                ["Avg Carbon Intensity", f"{mean_ci:.0f} g/kWh"],
                ["Avg CPU Utilization", f"{avg_cpu:.1f}%"]
            ]
            table = Table(data_table, hAlign='LEFT', colWidths=[180, 250])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.whitesmoke]),
            ]))
            Story.append(table)
            Story.append(Spacer(1, 16))

            Story.append(Paragraph("<b><font color='#cc99ff'>🧠 AI Summary of Observations</font></b>", styles["Heading3"]))
            summary_text = (
                "While overall energy efficiency is reasonable, carbon intensity remains above targets. "
                "CPU utilization suggests some servers are underutilized. Optimization through workload "
                "shifting and infrastructure tuning is recommended."
            )
            Story.append(Paragraph(summary_text, styles["BodyText"]))
            Story.append(Spacer(1, 16))

            Story.append(Paragraph("<b><font color='#ff6666'>🏁 Recommendations</font></b>", styles["Heading3"]))
            for r in recs:
                Story.append(Paragraph(r, styles["Normal"]))
                Story.append(Spacer(1, 4))

            Story.append(Spacer(1, 28))
            Story.append(Paragraph("<font size=9 color='#888888'>Built for UCD x Deloitte | Capstone 2025 🌱</font>", styles["Normal"]))

            doc.build(Story)
            buffer.seek(0)
            b64_pdf = base64.b64encode(buffer.read()).decode()
            st.download_button(
            label="📥 Download PDF Report",
            data=base64.b64decode(b64_pdf),
            file_name="Sustainability_Report.pdf",
            mime="application/pdf",
            key="download-pdf-button"
)       

        st.markdown("---")
        st.markdown("Built for UCD x Deloitte | Capstone 2025 🌱")

else:
    st.warning("Please upload a CSV file to begin.")