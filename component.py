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

     # Circular score setup
    radius = 15.9155
    circumference = 2 * 3.1416 * radius
    dash_offset = circumference * (1 - (score / 4))
    color = "#27ae60" if score == 4 else "#f1c40f" if score >= 2 else "#e74c3c"

    # Styled block
    st.markdown(
        f"""
        <style>
        .score-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .score-gauge {{
            margin-top: 5px;
            margin-bottom: 5px;
        }}
        .score-label {{
            font-size: 0.9rem;
            color: #aaa;
            margin-top: 6px;
        }}
        .score-description {{
            font-size: 0.85rem;
            text-align: center;
            color: #ccc;
            margin-top: 18px;
        }}
        </style>

        <div class="score-wrapper">
            <svg class="score-gauge" width="130" height="130" viewBox="0 0 36 36">
                <circle
                    cx="18"
                    cy="18"
                    r="{radius}"
                    fill="none"
                    stroke="#444"
                    stroke-width="2"
                    opacity="0.2"
                />
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
                <text x="18" y="20.5" fill="#ffffff" font-size="8" font-weight="bold" text-anchor="middle">
                    {score}/4
                </text>
            </svg>
            <div class="score-label">Sustainability Score</div>
        </div>

        <div class="score-description">
            ♻️ Monitor and optimize your IT infrastructure’s environmental impact.
        </div>
        """,
        unsafe_allow_html=True
    )


def render_kpi_cards(summary, co2_efficiency, pue, mean_ci):
    card_style = """
    <style>
    .kpi-container {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: space-between;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .kpi-card {
        background-color: #1f2630;
        border-radius: 14px;
        padding: 18px;
        width: calc(25% - 12px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        color: #fff;
        text-align: center;
        flex-grow: 1;
    }

    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
    }

    .kpi-label {
        font-size: 0.85rem;
        color: #ccc;
        margin-top: 6px;
    }

    @media (max-width: 900px) {
        .kpi-card {
            width: 48%;
        }
    }

    @media (max-width: 600px) {
        .kpi-card {
            width: 100%;
        }
    }
    </style>
    """

    st.markdown(card_style, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-value">{summary['total_co2']:.2f} kg</div>
            <div class="kpi-label">🧪 Total CO₂ Emissions</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{summary['total_energy']:.1f} kWh</div>
            <div class="kpi-label">⚡ Total Energy Used</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{summary['avg_cpu']:.1f}%</div>
            <div class="kpi-label">🖥️ Avg CPU Utilization</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{summary['breach_count']}</div>
            <div class="kpi-label">🚨 Breaches</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{co2_efficiency:.2f} kg/kWh</div>
            <div class="kpi-label">🌱 CO₂ Efficiency</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{pue:.2f}</div>
            <div class="kpi-label">🧊 Avg PUE</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{mean_ci:.0f} g/kWh</div>
            <div class="kpi-label">🔄 Shift Workloads</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    
