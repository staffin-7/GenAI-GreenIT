import streamlit as st

def render_sustainability_score(score: int):
    with st.expander("ℹ️ What does this score mean?"):
        st.markdown("""
        The **Sustainability Score (0–4)** reflects your infrastructure's environmental performance.

        A point is awarded for each of the following if it meets the configured threshold:
        
        - 🌱 **CO₂ Efficiency** (kg/kWh)
        - 🖥️ **Average CPU Utilization**
        - ❄️ **PUE (Power Usage Effectiveness)**
        - ⚡ **Carbon Intensity** (gCO₂/kWh)

        A score of **4** means optimal performance across all sustainability criteria.
        """)

    # Circle metrics
    radius = 15.9155
    circumference = 2 * 3.1416 * radius
    dash_offset = circumference * (1 - (score / 4))

    # Color by score level
    color = "#27ae60" if score == 4 else "#f1c40f" if score >= 2 else "#e74c3c"

    # Render circular progress with proper stroke math
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-top: 10px;">
            <svg width="130" height="130" viewBox="0 0 36 36">
                <!-- Background ring -->
                <circle
                    cx="18"
                    cy="18"
                    r="{radius}"
                    fill="none"
                    stroke="#555"
                    stroke-width="2"
                    opacity="0.15"
                />
                <!-- Progress ring -->
                <circle
                    cx="18"
                    cy="18"
                    r="{radius}"
                    fill="none"
                    stroke="{color}"
                    stroke-width="2.5"
                    stroke-linecap="round"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{dash_offset}"
                    transform="rotate(-90 18 18)"
                />
                <!-- Text label -->
                <text x="18" y="20.35" fill="#ffffff" font-size="8" font-weight="bold" text-anchor="middle">
                    {score}/4
                </text>
            </svg>
            <span style="color: #cccccc; font-size: 0.85rem; margin-top: 6px;">Sustainability Score</span>
        </div>
        """,
        unsafe_allow_html=True
    )
