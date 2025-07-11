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
    percentage = int((score / 4) * 100)
    color = "#27ae60" if score == 4 else "#f1c40f" if score >= 2 else "#e74c3c"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-top: 10px;">
            <svg width="130" height="130" viewBox="0 0 36 36">
                <path
                    d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#333"
                    stroke-width="2"
                    opacity="0.15"
                />
                <path
                    d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831"
                    fill="none"
                    stroke="{color}"
                    stroke-width="2"
                    stroke-dasharray="{percentage}, 100"
                />
                <text x="18" y="20.35" fill="white" font-size="8" font-weight="bold" text-anchor="middle">
                    {score}/4
                </text>
            </svg>
            <span style="color: gray; font-size: 0.85rem; margin-top: 6px;">Sustainability Score</span>
        </div>
        """,
        unsafe_allow_html=True
    )
