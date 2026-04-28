import os
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# ── API URL ────────────────────────────────────────────────────────────────────
if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
elif 'cloud_api_uri' in st.secrets:
    BASE_URI = st.secrets['cloud_api_uri']
else:
    BASE_URI = 'http://localhost:8000'

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grid Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Barlow+Condensed:wght@300;400;600;700;900&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Barlow Condensed', sans-serif;
    background-color: #080B0F;
    color: #C8D6E5;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Hero header ── */
.gi-header {
    background: linear-gradient(135deg, #080B0F 0%, #0D1117 50%, #080B0F 100%);
    border-bottom: 1px solid #1C2A3A;
    padding: 2rem 0 1.5rem 0;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.gi-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 80px,
        rgba(0, 212, 170, 0.015) 80px,
        rgba(0, 212, 170, 0.015) 81px
    );
    pointer-events: none;
}
.gi-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #FFFFFF;
    line-height: 1;
    margin: 0;
}
.gi-title span {
    color: #00D4AA;
}
.gi-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: #4A6278;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}
.gi-badge {
    display: inline-block;
    background: rgba(0, 212, 170, 0.1);
    border: 1px solid rgba(0, 212, 170, 0.3);
    color: #00D4AA;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    padding: 3px 10px;
    border-radius: 2px;
    margin-right: 8px;
    text-transform: uppercase;
}
.gi-badge-red {
    background: rgba(255, 80, 80, 0.1);
    border-color: rgba(255, 80, 80, 0.3);
    color: #FF5050;
}

/* ── Metric cards ── */
.metric-card {
    background: #0D1117;
    border: 1px solid #1C2A3A;
    border-top: 2px solid #00D4AA;
    padding: 1rem 1.2rem;
    position: relative;
}
.metric-card.danger { border-top-color: #FF5050; }
.metric-card.neutral { border-top-color: #4A6278; }
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: #4A6278;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
}
.metric-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: #4A6278;
    margin-top: 4px;
}

/* ── Section labels ── */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: #4A6278;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    border-left: 2px solid #00D4AA;
    padding-left: 8px;
    margin-bottom: 1rem;
}

/* ── Selectbox & widgets ── */
.stSelectbox label { color: #4A6278 !important; font-family: 'Space Mono', monospace !important; font-size: 0.65rem !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
.stSelectbox > div > div { background: #0D1117 !important; border-color: #1C2A3A !important; color: #C8D6E5 !important; border-radius: 0 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #00D4AA !important; }

/* ── Divider ── */
.gi-divider {
    border: none;
    border-top: 1px solid #1C2A3A;
    margin: 1.5rem 0;
}

/* ── Status dot ── */
.status-live {
    display: inline-block;
    width: 7px; height: 7px;
    background: #00D4AA;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── Footer ── */
.gi-footer {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: #1C2A3A;
    text-align: center;
    padding: 2rem 0 1rem 0;
    letter-spacing: 0.1em;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""
<div class="gi-header">
    <p class="gi-title">⚡ Grid<span>Intelligence</span></p>
    <p class="gi-subtitle">Day-Ahead Electricity Price Forecasting · DE-LU Bidding Zone</p>
    <div style="margin-top: 1rem;">
        <span class="gi-badge">Multi-Regime XGBoost</span>
        <span class="gi-badge">72h Horizon · 15min Resolution</span>
        <span class="gi-badge gi-badge-red">ENTSO-E · Open-Meteo · TTF Gas</span>
        <span style="font-family:'Space Mono',monospace; font-size:0.6rem; color:#2A3F52; margin-left:8px;">
            <span class="status-live"></span>LIVE · {now_str}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "prediction_data" not in st.session_state:
    st.session_state.prediction_data = None
if "backtest_data" not in st.session_state:
    st.session_state.backtest_data = None
if "backtest_days" not in st.session_state:
    st.session_state.backtest_days = 7

# ── Controls row ──────────────────────────────────────────────────────────────
col_view, col_days, col_spacer = st.columns([2, 2, 6])
with col_view:
    view = st.selectbox("VIEW", options=["Predict next 72 hours", "Backtest"], index=0)
with col_days:
    if view == "Backtest":
        days = st.selectbox("BACKTEST WINDOW", options=[1, 3, 7, 14], index=1)
        if days != st.session_state.backtest_days:
            st.session_state.backtest_days = days
            st.session_state.backtest_data = None

# ── Fetch data ─────────────────────────────────────────────────────────────────
if view == "Predict next 72 hours" and st.session_state.prediction_data is None:
    with st.spinner("Fetching forecast from model..."):
        try:
            response = requests.get(BASE_URI + '/predict', timeout=60)
            if response.status_code == 200:
                st.session_state.prediction_data = response.json()
        except Exception as e:
            st.error(f"API connection failed: {e}")

if view == "Backtest" and st.session_state.backtest_data is None:
    with st.spinner("Loading backtest data..."):
        try:
            response = requests.get(BASE_URI + f'/backtest?days={st.session_state.backtest_days}', timeout=60)
            if response.status_code == 200:
                st.session_state.backtest_data = response.json()
        except Exception as e:
            st.error(f"API connection failed: {e}")

# ── PREDICT VIEW ───────────────────────────────────────────────────────────────
if view == "Predict next 72 hours":
    data = st.session_state.prediction_data
    if data:
        predictions = data["predictions_15min"]
        timestamps = pd.to_datetime(data["timestamps"], utc=True)
        timestamps_berlin = timestamps.tz_convert('Europe/Berlin')
        df = pd.DataFrame({"timestamp": timestamps_berlin, "price": predictions})

        threshold = 140

        # ── Metrics ──
        min_val = min(predictions)
        max_val = max(predictions)
        avg_val = sum(predictions) / len(predictions)
        spike_hours = sum(1 for p in predictions if p > threshold) // 4
        min_ts = timestamps_berlin[predictions.index(min_val)].strftime("%a %d %b %H:%M")
        max_ts = timestamps_berlin[predictions.index(max_val)].strftime("%a %d %b %H:%M")

        st.markdown('<div class="section-label">FORECAST SUMMARY · NEXT 72H</div>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Min Price</div>
                <div class="metric-value">{min_val:.1f} <span style="font-size:1rem;color:#4A6278">€/MWh</span></div>
                <div class="metric-sub">{min_ts}</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            color_class = "danger" if max_val > threshold else ""
            st.markdown(f"""
            <div class="metric-card {color_class}">
                <div class="metric-label">Max Price</div>
                <div class="metric-value">{max_val:.1f} <span style="font-size:1rem;color:#4A6278">€/MWh</span></div>
                <div class="metric-sub">{max_ts}</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card neutral">
                <div class="metric-label">Avg Price</div>
                <div class="metric-value">{avg_val:.1f} <span style="font-size:1rem;color:#4A6278">€/MWh</span></div>
                <div class="metric-sub">72h window</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            spike_color = "danger" if spike_hours > 0 else ""
            st.markdown(f"""
            <div class="metric-card {spike_color}">
                <div class="metric-label">Spike Hours</div>
                <div class="metric-value">{spike_hours} <span style="font-size:1rem;color:#4A6278">h</span></div>
                <div class="metric-sub">&gt; {threshold} €/MWh threshold</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # ── Chart ──
        st.markdown('<div class="section-label">PRICE FORECAST · 15-MIN INTERVALS · EUROPE/BERLIN</div>', unsafe_allow_html=True)

        fig = go.Figure()

        # Negative price zone
        fig.add_hrect(y0=-150, y1=0,
            fillcolor="rgba(255,80,80,0.04)",
            line_width=0,
            annotation_text="NEGATIVE PRICE ZONE",
            annotation_position="top left",
            annotation_font_size=9,
            annotation_font_color="rgba(255,80,80,0.4)"
        )

        # Spike threshold
        fig.add_hline(
            y=threshold,
            line_dash="dash", line_color="rgba(255,80,80,0.5)", line_width=1,
            annotation_text=f"SPIKE THRESHOLD · {threshold} €/MWh",
            annotation_position="top right",
            annotation_font_color="rgba(255,80,80,0.6)",
            annotation_font_size=9
        )

        # Day dividers
        for ts in pd.date_range(
            df["timestamp"].min().floor("D") + pd.Timedelta(days=1),
            df["timestamp"].max().ceil("D"), freq="D"
        ):
            fig.add_vline(
                x=ts.timestamp() * 1000,
                line_dash="dot", line_color="rgba(255,255,255,0.08)", line_width=1,
                annotation_text=ts.strftime("%a %d %b").upper(),
                annotation_position="top",
                annotation_font_size=9,
                annotation_font_color="rgba(255,255,255,0.2)"
            )

        # Fill below line — split positive/negative
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["price"].clip(lower=0),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 170, 0.06)',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["price"].clip(upper=0),
            fill='tozeroy',
            fillcolor='rgba(255, 80, 80, 0.08)',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Main line
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["price"],
            mode="lines",
            name="Forecast",
            line=dict(color="#00D4AA", width=2),
            hovertemplate="<b>%{x|%a %d %b %H:%M}</b><br><b>%{y:.1f} €/MWh</b><extra></extra>"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=420,
            paper_bgcolor="#080B0F",
            plot_bgcolor="#0D1117",
            font=dict(family="Space Mono", size=10, color="#4A6278"),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.04)",
                linecolor="#1C2A3A",
                tickfont=dict(size=9),
                range=[df["timestamp"].min(), df["timestamp"].min() + pd.Timedelta(hours=72)]
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.04)",
                linecolor="#1C2A3A",
                tickfont=dict(size=9),
                range=[-80, max(300, max_val + 30)],
                ticksuffix=" €"
            ),
            showlegend=False,
            hovermode="x unified",
            margin=dict(l=50, r=30, t=20, b=40),
        )

        st.plotly_chart(fig, use_container_width=True)

        # ── Context callouts ──
        st.markdown('<div class="section-label">MARKET CONTEXT</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div style="background:#0D1117;border:1px solid #1C2A3A;padding:1rem;border-left:2px solid #00D4AA;">
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#4A6278;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;">Model</div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:600;color:#C8D6E5;">Multi-Regime XGBoost</div>
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#2A3F52;margin-top:4px;">Normal · Positive Spike · Negative Spike</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background:#0D1117;border:1px solid #1C2A3A;padding:1rem;border-left:2px solid #00D4AA;">
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#4A6278;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;">Data Sources</div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:600;color:#C8D6E5;">ENTSO-E · Open-Meteo</div>
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#2A3F52;margin-top:4px;">TTF Gas · WTI Oil · Brent</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div style="background:#0D1117;border:1px solid #1C2A3A;padding:1rem;border-left:2px solid #00D4AA;">
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#4A6278;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;">Coverage</div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:600;color:#C8D6E5;">DE-LU Bidding Zone</div>
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#2A3F52;margin-top:4px;">2018 – present · 15min resolution</div>
            </div>""", unsafe_allow_html=True)

# ── BACKTEST VIEW ──────────────────────────────────────────────────────────────
elif view == "Backtest":
    data = st.session_state.backtest_data
    if data:
        actual    = data["actual"]
        predicted = data["predicted"]
        timestamps = pd.to_datetime(data["timestamps"], utc=True)
        timestamps_berlin = timestamps.tz_convert('Europe/Berlin')
        df_bt = pd.DataFrame({"timestamp": timestamps_berlin, "actual": actual, "predicted": predicted})

        mae = sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)

        st.markdown('<div class="section-label">BACKTEST PERFORMANCE</div>', unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">MAE</div>
                <div class="metric-value">{mae:.2f} <span style="font-size:1rem;color:#4A6278">€/MWh</span></div>
                <div class="metric-sub">Mean Absolute Error</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card neutral">
                <div class="metric-label">Data Points</div>
                <div class="metric-value">{len(actual):,}</div>
                <div class="metric-sub">15-min intervals</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card neutral">
                <div class="metric-label">Window</div>
                <div class="metric-value">{st.session_state.backtest_days} <span style="font-size:1rem;color:#4A6278">days</span></div>
                <div class="metric-sub">historical evaluation</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">ACTUAL VS PREDICTED · EUROPE/BERLIN</div>', unsafe_allow_html=True)

        fig_bt = go.Figure()
        fig_bt.add_trace(go.Scatter(
            x=df_bt["timestamp"], y=df_bt["actual"],
            mode="lines", name="Actual",
            line=dict(color="#378ADD", width=2),
            hovertemplate="<b>Actual</b>: %{y:.1f} €/MWh<extra></extra>"
        ))
        fig_bt.add_trace(go.Scatter(
            x=df_bt["timestamp"], y=df_bt["predicted"],
            mode="lines", name="Predicted",
            line=dict(color="#00D4AA", width=1.5, dash="dash"),
            hovertemplate="<b>Predicted</b>: %{y:.1f} €/MWh<extra></extra>"
        ))
        fig_bt.update_layout(
            template="plotly_dark",
            height=420,
            paper_bgcolor="#080B0F",
            plot_bgcolor="#0D1117",
            font=dict(family="Space Mono", size=10, color="#4A6278"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="#1C2A3A", tickfont=dict(size=9)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="#1C2A3A", tickfont=dict(size=9), ticksuffix=" €"),
            hovermode="x unified",
            margin=dict(l=50, r=30, t=20, b=40),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                font=dict(family="Space Mono", size=9),
                bgcolor="rgba(0,0,0,0)"
            )
        )
        st.plotly_chart(fig_bt, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gi-footer">
    GRID INTELLIGENCE · LE WAGON BERLIN · APRIL 2026 · DE-LU ELECTRICITY MARKET FORECASTING
</div>
""", unsafe_allow_html=True)
