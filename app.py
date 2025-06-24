import streamlit as st
from backend import CarbonBackend
import altair as alt
import pandas as pd
from datetime import datetime
import base64

# Initialize backend
backend = CarbonBackend()

# Page config
st.set_page_config(
    page_title="CarbonWise | Sustainable IT Dashboard",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown(f"""
    <style>
        /* [Previous CSS content remains exactly the same] */
    </style>
    """, unsafe_allow_html=True)
    
    # Load JS
    with open("app.js") as f:
        st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

# File upload
def upload_file():
    st.sidebar.header("Data Configuration")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Server Data (CSV)", 
        type=["csv"],
        help="Upload your carbon-aware server dataset"
    )
    
    if uploaded_file:
        backend.load_data(uploaded_file)
        st.sidebar.success("Data loaded successfully!")
        return True
    return False

# Dashboard tabs - Now accepts filtered_data as parameter
def render_dashboard(filtered_data, summary):
    tabs = st.tabs(["📊 Overview", "📈 Trends", "🚨 Alerts", "🌍 Sustainability"])
    
    with tabs[0]:  # Overview
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Carbon Emissions by Server")
            if not filtered_data.empty:
                chart = alt.Chart(filtered_data).mark_bar().encode(
                    x=alt.X("Server_ID:N", title="Server", sort='-y'),
                    y=alt.Y("Total_CO2_kg:Q", title="CO₂ Emissions (kg)"),
                    color=alt.condition(
                        alt.datum.Threshold_Breach == 'Yes',
                        alt.value("#f07167"),
                        alt.value("#00a896")
                    ),
                    tooltip=["Server_ID", "Total_CO2_kg", "CPU_Utilisation (%)"]
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning("No data available for selected filters")
        
        with col2:
            st.subheader("Key Metrics")
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: var(--primary); margin-top: 0;">{summary['total_co2']:.1f} kg</h3>
                <p>Total CO₂ Emissions</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: var(--primary); margin-top: 0;">{summary['avg_cpu']:.1f}%</h3>
                <p>Avg CPU Utilization</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[1]:  # Trends
        st.subheader("Emissions Over Time")
        time_data = backend.get_time_series()
        if time_data is not None and not time_data.empty:
            trend_chart = alt.Chart(time_data).mark_area(
                interpolate='monotone',
                line={'color': '#00a896'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='white', offset=0),
                           alt.GradientStop(color='#00a896', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x='Date:T',
                y='Total_CO2_kg:Q',
                tooltip=['Date', 'Total_CO2_kg']
            ).properties(height=400)
            st.altair_chart(trend_chart, use_container_width=True)
        else:
            st.warning("No time series data available")
    
    with tabs[2]:  # Alerts
        st.subheader("Threshold Alerts")
        if not filtered_data.empty:
            breach_data = filtered_data[filtered_data['Threshold_Breach'] == 'Yes']
            
            if not breach_data.empty:
                for _, row in breach_data.iterrows():
                    with st.expander(f"🚨 Server {row['Server_ID']} - {row['Total_CO2_kg']:.2f} kg CO₂", expanded=True):
                        st.markdown(f"""
                        <div style="background: #fff5f5; padding: 15px; border-radius: 8px;">
                            <p><strong>Location:</strong> {row['Data_Center_Location']}</p>
                            <p><strong>CPU Utilization:</strong> {row['CPU_Utilisation (%)']}%</p>
                            <p><strong>Recommendations:</strong></p>
                            <ul>
                                <li>Migrate workloads to Norway servers</li>
                                <li>Schedule maintenance during off-peak hours</li>
                                <li>Consider hardware upgrades for efficiency</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("No threshold breaches detected!")
        else:
            st.warning("No data available for alerts")
    
    with tabs[3]:  # Sustainability
        st.subheader("Carbon Intensity Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            if backend.df is not None and not backend.df.empty:
                st.altair_chart(alt.Chart(backend.df).mark_boxplot().encode(
                    x='Data_Center_Location:N',
                    y='Carbon_Intensity_gCO2/kWh:Q',
                    color='Data_Center_Location:N'
                ), use_container_width=True)
            else:
                st.warning("No data available for comparison")
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>Sustainability Insights</h4>
                <p>Norway has the cleanest energy mix with 50 gCO₂/kWh</p>
                <p>Germany has the highest at 350 gCO₂/kWh</p>
                <p>Consider workload balancing strategies:</p>
                <ul>
                    <li>Geographical load shifting</li>
                    <li>Temporal workload scheduling</li>
                    <li>Server consolidation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Main app
def main():
    load_css()
    
    st.title("CarbonWise 🌿")
    st.markdown("### Sustainable IT Infrastructure Dashboard")
    
    if not upload_file():
        st.warning("Please upload a dataset to begin")
        return
    
    # Filters
    st.sidebar.header("Filters")
    selected_date = st.sidebar.selectbox(
        "Select Date",
        options=sorted(backend.df['Date'].unique()) if backend.df is not None else [],
        format_func=lambda x: pd.to_datetime(x).strftime('%b %d, %Y')
    )
    
    selected_locations = st.sidebar.multiselect(
        "Data Center Locations",
        options=backend.df['Data_Center_Location'].unique() if backend.df is not None else [],
        default=backend.df['Data_Center_Location'].unique() if backend.df is not None else []
    )
    
    # Thresholds
    st.sidebar.header("Threshold Settings")
    backend.co2_threshold = st.sidebar.slider(
        "CO₂ Threshold (kg)", 
        min_value=0.1, 
        max_value=5.0, 
        value=1.0, 
        step=0.1
    )
    
    backend.cpu_threshold = st.sidebar.slider(
        "CPU Threshold (%)", 
        min_value=50, 
        max_value=100, 
        value=80, 
        step=5
    )
    
    # Get filtered data
    if backend.df is not None:
        filtered_data = backend.get_filtered_data(selected_date, selected_locations)
        summary = backend.get_summary_stats(filtered_data)
        
        # Render dashboard with the required parameters
        render_dashboard(filtered_data, summary)
    else:
        st.error("No data available. Please upload a valid dataset.")
    
    # [Rest of the chat interface code remains the same]

if __name__ == "__main__":
    main()