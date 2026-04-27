import os
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# API URL
if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
else:
    BASE_URI = st.secrets['local_api_uri']
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
url = BASE_URI + 'predict'

# Page config
st.set_page_config(page_title="Grid Intelligence", page_icon="⚡", layout="wide")

# Title
st.title("⚡ Grid Intelligence")
st.subheader("Day-Ahead Electricity Price Prediction — DE-LU Market")

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #2ecc71;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
    }
    div.stButton > button:hover {
        background-color: #27ae60;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("Predict next 72 hours"):
    with st.spinner("Fetching prediction..."):
        response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        predictions = data["predictions_15min"]
        timestamps = pd.to_datetime(data["timestamps"])

        df = pd.DataFrame({
            "timestamp": timestamps,
            "price": predictions
        })

        fig = go.Figure()

        # ── Night shading (22:00 - 06:00) ────────────────────────────────────
        for ts in pd.date_range(df["timestamp"].min().floor("D"),
                                df["timestamp"].max().ceil("D"), freq="D"):
            night_start = pd.Timestamp(f"{ts.date()} 22:00:00")
            night_end   = pd.Timestamp(f"{ts.date()} 06:00:00") + pd.Timedelta(days=1)
            fig.add_vrect(
                x0=night_start, x1=min(night_end, df["timestamp"].max()),
                fillcolor="rgba(100,100,100,0.15)", line_width=0,
                annotation_text="Night", annotation_position="top left",
                annotation_font_size=10, annotation_font_color="gray"
            )

        # ── Peak hour shading (07:00-09:00 and 17:00-20:00) ──────────────────
        for ts in pd.date_range(df["timestamp"].min().floor("D"),
                                df["timestamp"].max().ceil("D"), freq="D"):
            for h_start, h_end, label in [("07:00", "09:00", "Morning Peak"),
                                           ("17:00", "20:00", "Evening Peak")]:
                fig.add_vrect(
                    x0=pd.Timestamp(f"{ts.date()} {h_start}"),
                    x1=pd.Timestamp(f"{ts.date()} {h_end}"),
                    fillcolor="rgba(255,165,0,0.1)", line_width=0,
                    annotation_text=label, annotation_position="top left",
                    annotation_font_size=9, annotation_font_color="orange"
                )

        # ── Spike threshold line (150 EUR/MWh) ───────────────────────────────
        threshold = 135
        fig.add_hline(

            # only one parameter
            y=threshold, line_dash="dash", line_color="red", line_width=1,
            annotation_text=f"Spike threshold ({threshold} EUR/MWh)",
            annotation_position="top right",
            annotation_font_color="red"
        )

        # ── Midnight vertical lines ───────────────────────────────────────────
        for ts in pd.date_range(df["timestamp"].min().floor("D") + pd.Timedelta(days=1),
                                df["timestamp"].max().ceil("D"), freq="D"):
            fig.add_vline(
                x=ts.timestamp() * 1000,
                line_dash="dot", line_color="rgba(255,255,255,0.3)", line_width=1,
                annotation_text=ts.strftime("%a %d %b"),
                annotation_position="top",
                annotation_font_size=11,
                annotation_font_color="white"
            )

        # ── Price line (color: green→yellow→red) ─────────────────────────────
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["price"],
            mode="lines",
            name="Predicted Price",
            line=dict(color="#00d4aa", width=2),
            hovertemplate="<b>%{x|%a %d %b %H:%M}</b><br>Price: %{y:.1f} EUR/MWh<extra></extra>"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=500,
            xaxis_title="Time",
            yaxis_title="EUR/MWh",
            showlegend=False,
            hovermode="x unified",
            margin=dict(l=40, r=40, t=40, b=40),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        )

        st.plotly_chart(fig, use_container_width=True)

        # ── Metrics ───────────────────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Min Price",  f"{min(predictions):.2f} EUR/MWh")
        col2.metric("Max Price",  f"{max(predictions):.2f} EUR/MWh")
        col3.metric("Avg Price",  f"{sum(predictions)/len(predictions):.2f} EUR/MWh")
        spike_hours = sum(1 for p in predictions if p > 150) // 4
        col4.metric("Spike Hours", f"{spike_hours}h")

    else:
        st.error(f"API Error: {response.status_code}")
