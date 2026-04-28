import os
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# API URL
if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
elif 'cloud_api_uri' in st.secrets:
    BASE_URI = st.secrets['cloud_api_uri']
else:
    BASE_URI = 'http://localhost:8000'

st.set_page_config(page_title="Grid Intelligence", page_icon="⚡", layout="wide")
st.title("⚡ Grid Intelligence V2")
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

# ── Session state init ─────────────────────────────────────────────────────────
if "prediction_data" not in st.session_state:
    st.session_state.prediction_data = None
if "backtest_data" not in st.session_state:
    st.session_state.backtest_data = None
if "backtest_days" not in st.session_state:
    st.session_state.backtest_days = 7

col_chart, col_controls = st.columns([3, 1])

with col_controls:
    view = st.selectbox("Select view", options=["Predict next 72 hours", "Backtest"], index=0)

    if view == "Backtest":
        days = st.selectbox("Days to backtest", options=[1, 3, 7, 14], index=1)
        # Re-fetch if days changed
        if days != st.session_state.backtest_days:
            st.session_state.backtest_days = days
            st.session_state.backtest_data = None

# ── Auto-fetch prediction on first load ───────────────────────────────────────
if view == "Predict next 72 hours" and st.session_state.prediction_data is None:
    with st.spinner("Fetching prediction..."):
        response = requests.get(BASE_URI + '/predict')
        if response.status_code == 200:
            st.session_state.prediction_data = response.json()

# ── Auto-fetch backtest when selected ─────────────────────────────────────────
if view == "Backtest" and st.session_state.backtest_data is None:
    with st.spinner("Loading backtest..."):
        response = requests.get(BASE_URI + f'/backtest?days={st.session_state.backtest_days}')
        if response.status_code == 200:
            st.session_state.backtest_data = response.json()

# ── Render charts ──────────────────────────────────────────────────────────────
with col_chart:

    if view == "Predict next 72 hours":
        data = st.session_state.prediction_data
        if data:
            predictions = data["predictions_15min"]
            timestamps = (pd.to_datetime(data["timestamps"], utc=True))

            timestamps_berlin = timestamps.tz_convert('Europe/Berlin')
            df = pd.DataFrame({"timestamp": timestamps_berlin, "price": predictions})
            fig = go.Figure()


            threshold = 140
            fig.add_hline(
                y=threshold, line_dash="dash", line_color="red", line_width=1,
                annotation_text=f"Spike threshold ({threshold} EUR/MWh)",
                annotation_position="top right", annotation_font_color="red"
            )

            for ts in pd.date_range(df["timestamp"].min().floor("D") + pd.Timedelta(days=1), df["timestamp"].max().ceil("D"), freq="D"):
                fig.add_vline(
                    x=ts.timestamp() * 1000,
                    line_dash="dot", line_color="rgba(255,255,255,0.3)", line_width=1,
                    annotation_text=ts.strftime("%a %d %b"),
                    annotation_position="top",
                    annotation_font_size=11, annotation_font_color="white"
                )

            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=df["price"],
                mode="lines", name="Predicted Price",
                line=dict(color="#00d4aa", width=2),
                hovertemplate="<b>%{x|%a %d %b %H:%M}</b><br>Price: %{y:.1f} EUR/MWh<extra></extra>"
            ))

            fig.update_layout(
                template="plotly_dark", height=500,
                xaxis_title="Time", yaxis_title="EUR/MWh",
                showlegend=False, hovermode="x unified",
                margin=dict(l=40, r=40, t=40, b=40),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)", range=[-100, 300]),
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)",
                           range=[df["timestamp"].min(), df["timestamp"].min() + pd.Timedelta(hours=72)])
            )

            st.plotly_chart(fig, use_container_width=True)

            col1, col2, col3, col4 = st.columns(4)
            min_idx = predictions.index(min(predictions))
            min_ts = timestamps_berlin[min_idx].strftime("%a %d %b %H:%M")
            col1.metric("Min Price", f"{min(predictions):.2f} EUR/MWh", delta=min_ts, delta_color="off")

            #col2.metric("Max Price",  f"{max(predictions):.2f} EUR/MWh")
            max_idx = predictions.index(max(predictions))
            max_ts = timestamps_berlin[max_idx].strftime("%a %d %b %H:%M")
            col2.metric("Max Price", f"{max(predictions):.2f} EUR/MWh", delta=max_ts, delta_color="off")


            col3.metric("Avg Price",  f"{sum(predictions)/len(predictions):.2f} EUR/MWh")
            spike_hours = sum(1 for p in predictions if p > threshold) // 4
            col4.metric("Spike Hours", f"{spike_hours}h")

    elif view == "Backtest":
        data = st.session_state.backtest_data
        if data:
            actual    = data["actual"]
            predicted = data["predicted"]
            timestamps = pd.to_datetime(data["timestamps"], utc=True)

            timestamps_berlin = timestamps.tz_convert('Europe/Berlin')
            df_bt = pd.DataFrame({"timestamp": timestamps_berlin, "actual": actual, "predicted": predicted})

            fig_bt = go.Figure()
            fig_bt.add_trace(go.Scatter(x=df_bt["timestamp"], y=df_bt["actual"],
                mode="lines", name="Actual", line=dict(color="#378ADD", width=2)))
            fig_bt.add_trace(go.Scatter(x=df_bt["timestamp"], y=df_bt["predicted"],
                mode="lines", name="Predicted", line=dict(color="#00d4aa", width=2, dash="dash")))

            fig_bt.update_layout(
                template="plotly_dark", height=500,
                xaxis_title="Time", yaxis_title="EUR/MWh",
                hovermode="x unified",
                margin=dict(l=40, r=40, t=40, b=40),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)", range=[-500, 350]),
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )

            st.plotly_chart(fig_bt, use_container_width=True)

            mae = sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)
            col1, col2 = st.columns(2)
            col1.metric("MAE", f"{mae:.2f} EUR/MWh")
            col2.metric("Rows", len(actual))
