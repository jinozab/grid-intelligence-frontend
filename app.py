import os
import requests
import pandas as pd
import numpy as np
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

st.set_page_config(
    page_title="Grid Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Barlow+Condensed:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Barlow Condensed', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

.gi-header {
    border-bottom: 2px solid rgba(0,196,154,0.3);
    padding: 1.8rem 0 1.4rem 0;
    margin-bottom: 1.5rem;
}
.gi-title {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-color);
    line-height: 1;
    margin: 0;
}

.gi-title span { color: #00C49A; }
.gi-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem; color: var(--text-color); opacity: 0.5;
    letter-spacing: 0.14em; text-transform: uppercase; margin-top: 0.4rem;
}
.gi-badge {
    display: inline-block;
    background: rgba(0,196,154,0.12); border: 1px solid rgba(0,196,154,0.35);
    color: #00C49A; font-family: 'Space Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.1em;
    padding: 3px 10px; border-radius: 3px; margin-right: 6px; text-transform: uppercase;
}
.gi-badge-red { background: rgba(255,100,80,0.12); border-color: rgba(255,100,80,0.35); color: #FF8070; }
.status-live {
    display: inline-block; width: 7px; height: 7px;
    background: #00C49A; border-radius: 50%; margin-right: 5px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }

.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-top: 3px solid #00C49A;
    border-radius: 6px; padding: 1.2rem 1.3rem;
    min-height: 170px;
}
.metric-card.danger  { border-top-color: #E84545; }
.metric-card.warning { border-top-color: #F59E0B; }
.metric-card.neutral { border-top-color: rgba(255,255,255,0.2); }
.metric-icon { width: 28px; height: 28px; margin-bottom: 10px; }
.metric-label {
    font-family: 'Space Mono', monospace; font-size: 0.6rem;
    color: var(--text-color); opacity: 0.45;
    letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 4px;
}
.metric-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.4rem; font-weight: 700;
    color: var(--text-color); line-height: 1;
}
.metric-unit { font-size: 1.1rem; color: var(--text-color); opacity: 0.45; font-weight: 400; }
.metric-sub {
    font-family: 'Space Mono', monospace; font-size: 1.0rem;
    color: var(--text-color); opacity: 0.45; margin-top: 6px;
}

.section-label {
    font-family: 'Space Mono', monospace; font-size: 1.0rem;
    color: var(--text-color); opacity: 0.4;
    letter-spacing: 0.18em; text-transform: uppercase;
    border-left: 3px solid #00C49A; padding-left: 8px; margin-bottom: 1rem;
}

.biz-table {
    width: 100%; border-collapse: collapse;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px; overflow: hidden;
    font-family: 'Barlow Condensed', sans-serif;
}
.biz-table thead tr { background: rgba(255,255,255,0.06); }
.biz-table thead th {
    font-family: 'Space Mono', monospace; font-size: 1.0rem;
    letter-spacing: 0.14em; text-transform: uppercase;
    padding: 10px 16px; text-align: left; font-weight: 400;
    color: var(--text-color); opacity: 0.4;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.biz-table tbody tr { border-bottom: 1px solid rgba(255,255,255,0.05); }
.biz-table tbody tr:last-child { border-bottom: none; }
.biz-table tbody tr:hover { background: rgba(255,255,255,0.04); }
.biz-table td { padding: 11px 16px; font-size: 1.2rem; color: var(--text-color); vertical-align: middle; }
.biz-table td:first-child { font-size: 1.2rem; color: var(--text-color); opacity: 0.55; width: 28%; }
.biz-table td:nth-child(2) { font-weight: 600; width: 30%; }
.biz-table td.positive { color: #00C49A !important; opacity: 1; }
.biz-table td.negative { color: #E84545 !important; opacity: 1; }
.biz-table td.warning  { color: #F59E0B !important; opacity: 1; }

.stSelectbox label {
    color: var(--text-color) !important; opacity: 0.5;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.58rem !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

.gi-footer {
    font-family: 'Space Mono', monospace; font-size: 1.0rem;
    color: var(--text-color); opacity: 0.2; text-align: center;
    padding: 2rem 0 1rem 0; letter-spacing: 0.1em;
    border-top: 1px solid rgba(255,255,255,0.08); margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ── Business Labels for SHAP Features ─────────────────────────────────────────
FEATURE_LABELS = {
    "price_lag_1":              "Price 15 min ago",
    "price_lag_4":              "Price 1h ago",
    "price_lag_12":             "Price 3h ago",
    "price_lag_24":             "Price 6h ago",
    "price_lag_96":             "Price 24h ago",
    "price_lag_672":            "Price 1 week ago",
    "price_roll_mean_24":       "Avg Price last 6h",
    "price_roll_mean_96":       "Avg Price last 24h",
    "price_roll_mean_672":      "Avg Price last week",
    "price_roll_std_4":         "Price Volatility 1h",
    "price_roll_std_96":        "Price Volatility 24h",
    "generation_renewable":                      "Renewable Generation",
    "generation_renewable_lag_1":                "Renewable 15 min ago",
    "generation_renewable_lag_4":                "Renewable 1h ago",
    "generation_renewable_lag_24":               "Renewable 6h ago",
    "generation_renewable_lag_96":               "Renewable 24h ago",
    "generation_renewable_lag_672":              "Renewable 1 week ago",
    "generation_renewable_roll_mean_24":         "Avg Renewable last 6h",
    "generation_renewable_roll_mean_96":         "Avg Renewable last 24h",
    "generation_renewable_roll_mean_672":        "Avg Renewable last week",
    "generation_renewable_roll_std_24":          "Renewable Volatility 24h",
    "generation_renewable_roll_std_96":          "Renewable Volatility 96h",
    "generation_non_renewable":                  "Conventional Generation",
    "generation_non_renewable_lag_1":            "Conventional 15 min ago",
    "generation_non_renewable_lag_4":            "Conventional 1h ago",
    "generation_non_renewable_lag_24":           "Conventional 6h ago",
    "generation_non_renewable_lag_96":           "Conventional 24h ago",
    "generation_non_renewable_lag_672":          "Conventional 1 week ago",
    "generation_non_renewable_roll_mean_24":     "Avg Conventional last 6h",
    "generation_non_renewable_roll_mean_96":     "Avg Conventional last 24h",
    "generation_non_renewable_roll_mean_672":    "Avg Conventional last week",
    "generation_non_renewable_roll_std_24":      "Conventional Volatility 24h",
    "generation_non_renewable_roll_std_96":      "Conventional Volatility 96h",
    "consumption":                   "Power Consumption",
    "consumption_lag_1":             "Consumption 15 min ago",
    "consumption_lag_4":             "Consumption 1h ago",
    "consumption_lag_24":            "Consumption 6h ago",
    "consumption_lag_96":            "Consumption 24h ago",
    "consumption_lag_672":           "Consumption 1 week ago",
    "consumption_roll_mean_24":      "Avg Consumption last 6h",
    "consumption_roll_mean_96":      "Avg Consumption last 24h",
    "consumption_roll_mean_672":     "Avg Consumption last week",
    "consumption_roll_std_24":       "Consumption Volatility 24h",
    "consumption_roll_std_96":       "Consumption Volatility 96h",
    "wind_onshore":                  "Onshore Wind Power",
    "wind_onshore_lag_1":            "Wind 15 min ago",
    "wind_onshore_lag_12":           "Wind 3h ago",
    "wind_onshore_lag_24":           "Wind 6h ago",
    "wind_onshore_lag_96":           "Wind 24h ago",
    "wind_onshore_lag_672":          "Wind 1 week ago",
    "wind_onshore_roll_mean_24":     "Avg Wind last 6h",
    "wind_onshore_roll_mean_96":     "Avg Wind last 24h",
    "wind_onshore_roll_mean_672":    "Avg Wind last week",
    "wind_onshore_roll_std_24":      "Wind Volatility 24h",
    "wind_onshore_roll_std_96":      "Wind Volatility 96h",
    "temperature_c_observed":                        "Temperature",
    "temperature_c_observed_lag_1":                  "Temperature 15 min ago",
    "temperature_c_observed_lag_4":                  "Temperature 1h ago",
    "temperature_c_observed_lag_96":                 "Temperature 24h ago",
    "temperature_c_observed_lag_672":                "Temperature 1 week ago",
    "temperature_c_observed_roll_mean_24":           "Avg Temperature last 6h",
    "temperature_c_observed_roll_mean_96":           "Avg Temperature last 24h",
    "temperature_c_observed_roll_mean_672":          "Avg Temperature last week",
    "temperature_c_observed_roll_std_24":            "Temperature Volatility 24h",
    "shortwave_radiation_wm2_observed":              "Solar Radiation",
    "shortwave_radiation_wm2_observed_lag_1":        "Solar Radiation 15 min ago",
    "shortwave_radiation_wm2_observed_lag_4":        "Solar Radiation 1h ago",
    "shortwave_radiation_wm2_observed_lag_96":       "Solar Radiation 24h ago",
    "shortwave_radiation_wm2_observed_lag_672":      "Solar Radiation 1 week ago",
    "shortwave_radiation_wm2_observed_roll_mean_24": "Avg Solar Radiation last 6h",
    "shortwave_radiation_wm2_observed_roll_mean_96": "Avg Solar Radiation last 24h",
    "shortwave_radiation_wm2_observed_roll_mean_672":"Avg Solar Radiation last week",
    "cloud_cover_percent_observed":                  "Cloud Cover",
    "cloud_cover_percent_observed_lag_96":           "Cloud Cover 24h ago",
    "cloud_cover_percent_observed_lag_672":          "Cloud Cover 1 week ago",
    "cloud_cover_percent_observed_roll_mean_24":     "Avg Cloud Cover last 6h",
    "cloud_cover_percent_observed_roll_mean_96":     "Avg Cloud Cover last 24h",
    "cloud_cover_percent_observed_roll_mean_672":    "Avg Cloud Cover last week",
    "wind_speed_ms_observed":                        "Wind Speed",
    "wind_speed_ms_observed_lag_96":                 "Wind Speed 24h ago",
    "wind_speed_ms_observed_lag_672":                "Wind Speed 1 week ago",
    "wind_speed_ms_observed_roll_mean_24":           "Avg Wind Speed last 6h",
    "wind_speed_ms_observed_roll_mean_96":           "Avg Wind Speed last 24h",
    "wind_speed_ms_observed_roll_mean_672":          "Avg Wind Speed last week",
    "wind_speed_ms_observed_roll_std_96":            "Wind Speed Volatility",
    "wti_oil":                   "WTI Oil Price",
    "wti_oil_lag_1":             "Oil Price 15 min ago",
    "wti_oil_lag_4":             "Oil Price 1h ago",
    "wti_oil_lag_96":            "Oil Price 24h ago",
    "wti_oil_lag_672":           "Oil Price 1 week ago",
    "wti_oil_roll_mean_24":      "Avg Oil Price last 6h",
    "wti_oil_roll_mean_96":      "Avg Oil Price last 24h",
    "wti_oil_roll_mean_672":     "Avg Oil Price last week",
    "wti_oil_roll_std_24":       "Oil Price Volatility 24h",
    "wti_oil_roll_std_96":       "Oil Price Volatility 96h",
    "natural_gas":               "Natural Gas Price",
    "natural_gas_lag_1":         "Gas Price 15 min ago",
    "natural_gas_lag_4":         "Gas Price 1h ago",
    "natural_gas_lag_96":        "Gas Price 24h ago",
    "natural_gas_lag_672":       "Gas Price 1 week ago",
    "natural_gas_roll_mean_24":  "Avg Gas Price last 6h",
    "natural_gas_roll_mean_96":  "Avg Gas Price last 24h",
    "natural_gas_roll_mean_672": "Avg Gas Price last week",
    "natural_gas_roll_std_24":   "Gas Price Volatility 24h",
    "natural_gas_roll_std_96":   "Gas Price Volatility 96h",
    "ttf_gas":                   "TTF Gas Price",
    "ttf_gas_lag_1":             "TTF Gas 15 min ago",
    "ttf_gas_lag_4":             "TTF Gas 1h ago",
    "ttf_gas_lag_96":            "TTF Gas 24h ago",
    "ttf_gas_lag_672":           "TTF Gas 1 week ago",
    "ttf_gas_roll_mean_24":      "Avg TTF Gas last 6h",
    "ttf_gas_roll_mean_96":      "Avg TTF Gas last 24h",
    "ttf_gas_roll_mean_672":     "Avg TTF Gas last week",
    "ttf_gas_roll_std_24":       "TTF Gas Volatility 24h",
    "ttf_gas_roll_std_96":       "TTF Gas Volatility 96h",
    "hour":                      "Time of Day",
    "day_of_week":               "Day of Week",
    "day_of_year":               "Season",
    "month":                     "Month",
    "quarter_hour":              "Quarter Hour",
    "renewable_ratio":           "Renewable Share in Mix",
    "renewable_hour":            "Solar Time-of-Day Effect",
    "renewable_season":          "Solar Seasonal Effect",
    "holiday_consumption":       "Holiday Consumption",
    "bridge_consumption":        "Bridge Day Consumption",
    "oil_nonrenewable":          "Oil × Conventional Output",
    "gas_nonrenewable":          "Gas × Conventional Output",
    "peak_demand":               "Peak Demand",
    "renewable_consumption":     "Renewable × Consumption",
    "oil_gas_ratio":             "Oil/Gas Ratio",
}

ICON_DOWN = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="#00C49A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>"""
ICON_UP = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="#E84545" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>"""
ICON_AVG = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="22" y1="12" x2="2" y2="12"/>
  <path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/></svg>"""
ICON_SPIKE = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
  <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>"""

now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""
<div class="gi-header">
    <p class="gi-title">⚡ Grid<span>Intelligence</span></p>
    <p class="gi-subtitle">Day-Ahead Electricity Price Forecasting · DE-LU Bidding Zone</p>
    <div style="margin-top:1rem;">
        <span class="gi-badge">Multi-Regime XGBoost</span>
        <span class="gi-badge">72h · 15min Resolution</span>
        <span class="gi-badge gi-badge-red">ENTSO-E · Open-Meteo · TTF</span>
        <span style="font-family:'Space Mono',monospace;font-size:1.0rem;color:rgba(255,255,255,0.25);margin-left:10px;">
            <span class="status-live"></span>LIVE · {now_str}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in [
    ("prediction_data", None), ("backtest_data", None), ("backtest_days", 7),
    ("energy_mix_data", None), ("explain_data", None)
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Controls ──────────────────────────────────────────────────────────────────
col_view, col_days, _ = st.columns([2, 2, 6])
with col_view:
    view = st.selectbox("VIEW", options=["Predict next 72 hours", "Backtest", "Energy Mix"], index=0)
with col_days:
    if view == "Backtest":
        days = st.selectbox("BACKTEST WINDOW", options=[1, 3, 7, 14], index=1)
        if days != st.session_state.backtest_days:
            st.session_state.backtest_days = days
            st.session_state.backtest_data = None

# ── Fetch ──────────────────────────────────────────────────────────────────────
if view == "Predict next 72 hours" and st.session_state.prediction_data is None:
    with st.spinner("Fetching forecast..."):
        try:
            r = requests.get(BASE_URI + '/predict', timeout=60)
            if r.status_code == 200:
                st.session_state.prediction_data = r.json()
        except Exception as e:
            st.error(f"API connection failed: {e}")

if view == "Predict next 72 hours" and st.session_state.explain_data is None:
    with st.spinner("Computing SHAP explanations..."):
        try:
            r = requests.get(BASE_URI + '/explain', timeout=60)
            if r.status_code == 200:
                st.session_state.explain_data = r.json()
        except Exception as e:
            st.warning(f"SHAP explanation unavailable: {e}")

if view == "Backtest" and st.session_state.backtest_data is None:
    with st.spinner("Loading backtest..."):
        try:
            r = requests.get(BASE_URI + f'/backtest?days={st.session_state.backtest_days}', timeout=60)
            if r.status_code == 200:
                st.session_state.backtest_data = r.json()
        except Exception as e:
            st.error(f"API connection failed: {e}")

if view == "Energy Mix" and st.session_state.energy_mix_data is None:
    with st.spinner("Loading energy mix..."):
        try:
            r = requests.get(BASE_URI + '/energy-mix?days=7', timeout=60)
            if r.status_code == 200:
                st.session_state.energy_mix_data = r.json()
        except Exception as e:
            st.error(f"API connection failed: {e}")

# ── PREDICT VIEW ───────────────────────────────────────────────────────────────
if view == "Predict next 72 hours":
    data = st.session_state.prediction_data
    if data:
        predictions = data["predictions_15min"]
        timestamps  = pd.to_datetime(data["timestamps"], utc=True)
        timestamps_berlin = timestamps.tz_convert('Europe/Berlin')
        df = pd.DataFrame({"timestamp": timestamps_berlin, "price": predictions})
        threshold = 140

        min_val     = min(predictions)
        max_val     = max(predictions)
        avg_val     = sum(predictions) / len(predictions)
        std_val     = float(np.std(predictions))
        spike_hours = sum(1 for p in predictions if p > threshold) // 4
        neg_hours   = sum(1 for p in predictions if p < 0) // 4
        min_ts = timestamps_berlin[predictions.index(min_val)].strftime("%a %d %b %H:%M")
        max_ts = timestamps_berlin[predictions.index(max_val)].strftime("%a %d %b %H:%M")

        window = 16
        best_charge_start = int(np.argmin([sum(predictions[i:i+window]) for i in range(len(predictions)-window)]))
        best_charge_ts    = timestamps_berlin[best_charge_start].strftime("%a %d %b %H:%M")
        best_charge_end   = timestamps_berlin[min(best_charge_start+window, len(timestamps_berlin)-1)].strftime("%H:%M")
        best_charge_price = predictions[best_charge_start]

        window2 = 8
        best_discharge_start = int(np.argmax([sum(predictions[i:i+window2]) for i in range(len(predictions)-window2)]))
        best_discharge_ts    = timestamps_berlin[best_discharge_start].strftime("%a %d %b %H:%M")
        best_discharge_end   = timestamps_berlin[min(best_discharge_start+window2, len(timestamps_berlin)-1)].strftime("%H:%M")
        best_discharge_price = predictions[best_discharge_start]

        # ── SHAP Recommendation ───────────────────────────────────────────
        action = "🟡 Neutral · Monitor"
        explain = st.session_state.get("explain_data")
        if explain:
            avg_shap = sum(f["shap_value"] for f in explain["top_features"]) / len(explain["top_features"])
            if avg_shap < -5:
                action = "🟢 Low price · Charge now"
            elif avg_shap > 5:
                action = "🔴 High price · Reduce load"

        st.markdown('<div class="section-label">FORECAST SUMMARY · NEXT 72H</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class="metric-card">{ICON_DOWN}
                <div class="metric-label">Min Price</div>
                <div class="metric-value">{min_val:.1f} <span class="metric-unit">€/MWh</span></div>
                <div class="metric-sub">{min_ts}</div></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-card {'danger' if max_val > threshold else ''}">{ICON_UP}
                <div class="metric-label">Max Price</div>
                <div class="metric-value">{max_val:.1f} <span class="metric-unit">€/MWh</span></div>
                <div class="metric-sub">{max_ts}</div></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="metric-card neutral">{ICON_AVG}
                <div class="metric-label">Avg Price</div>
                <div class="metric-value">{avg_val:.1f} <span class="metric-unit">€/MWh</span></div>
                <div class="metric-sub">72h window</div></div>""", unsafe_allow_html=True)
        with m4:
            if avg_shap < -5:
                icon_outlook = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="#00C49A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>"""
            elif avg_shap > 5:
                icon_outlook = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="#E84545" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>"""
            else:
                icon_outlook = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="22" y1="12" x2="2" y2="12"/></svg>"""

            st.markdown(f"""<div class="metric-card {'warning' if spike_hours > 0 else 'neutral'}">{icon_outlook}
                <div class="metric-label">Market Outlook</div>
                <div style="font-family:'Barlow Condensed',sans-serif; font-size:2rem; font-weight:700; line-height:1; margin-top:0.5rem;">
                    {action}
                </div>
    </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">PRICE FORECAST · 15-MIN INTERVALS · EUROPE/BERLIN</div>', unsafe_allow_html=True)

        col_chart, col_space, col_shap = st.columns([4, 0.3, 2])

        with col_chart:
            fig = go.Figure()
            fig.add_hrect(y0=-200, y1=0, fillcolor="rgba(232,69,69,0.05)", line_width=0,
                annotation_text="NEGATIVE PRICE ZONE", annotation_position="top left",
                annotation_font_size=9, annotation_font_color="rgba(232,69,69,0.4)")
            fig.add_hline(y=threshold, line_dash="dash", line_color="rgba(232,69,69,0.4)", line_width=1,
                annotation_text=f"SPIKE · {threshold} €/MWh", annotation_position="top right",
                annotation_font_color="rgba(232,69,69,0.5)", annotation_font_size=9)
            for ts in pd.date_range(df["timestamp"].min().floor("D") + pd.Timedelta(days=1),
                                    df["timestamp"].max().ceil("D"), freq="D"):
                fig.add_vline(x=ts.timestamp()*1000, line_dash="dot",
                    line_color="rgba(255,255,255,0.15)", line_width=1,
                    annotation_text=ts.strftime("%a %d %b").upper(),
                    annotation_position="top", annotation_font_size=9,
                    annotation_font_color="rgba(255,255,255,0.3)")
            fig.add_trace(go.Scatter(x=df["timestamp"], y=df["price"].clip(lower=0),
                fill='tozeroy', fillcolor='rgba(0,196,154,0.08)',
                line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=df["timestamp"], y=df["price"].clip(upper=0),
                fill='tozeroy', fillcolor='rgba(232,69,69,0.08)',
                line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=df["timestamp"], y=df["price"],
                mode="lines", line=dict(color="#00C49A", width=2),
                hovertemplate="<b>%{x|%a %d %b %H:%M}</b><br><b>%{y:.1f} €/MWh</b><extra></extra>"))
            y_min = min(min(predictions) - 20, -20)
            y_max = max(max(predictions) + 10, 120)
            fig.update_layout(
                template="plotly_dark", height=400,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Space Mono", size=13, color="rgba(255,255,255,0.4)"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)",
                           tickfont=dict(size=13),
                           range=[df["timestamp"].min(), df["timestamp"].min() + pd.Timedelta(hours=72)]),

                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)",
                           tickfont=dict(size=13), range=[y_min, y_max], ticksuffix=" €"),
                showlegend=False, hovermode="x unified", margin=dict(l=50, r=30, t=20, b=40))
            st.plotly_chart(fig, use_container_width=True)

        with col_shap:
            explain = st.session_state.get("explain_data")
            if explain:
                features = explain["top_features"]
                regime_map = {0: "Normal", 1: "Positive Spike", 2: "Negative Spike"}
                regime_label = regime_map.get(explain.get("regime", 0), "Normal")

                weather, timing, commodities, price_hist = [], [], [], []
                seen_base = set()  # verhindert Duplikate

                for f in features:
                    name = f["feature"]
                    val  = f["shap_value"]

                    # Basis-Feature-Name extrahieren (ohne _lag_96, _roll_mean etc.)
                    base = name.split("_lag_")[0].split("_roll_")[0]

                    # Jeden Basis-Feature nur einmal zeigen
                    if base in seen_base:
                        continue
                    seen_base.add(base)

                    direction = "↑ pushing price UP" if val > 0 else "↓ pushing price DOWN"
                    label = FEATURE_LABELS.get(name, name)
                    entry = f"{label} · {direction}"

                    if any(x in name for x in ["solar", "shortwave", "cloud", "temperature", "wind_speed"]):
                        weather.append(entry)
                    elif any(x in name for x in ["hour", "day_of_week", "day_of_year", "month", "quarter_hour"]):
                        timing.append(entry)
                    elif any(x in name for x in ["gas", "oil", "ttf", "wti"]):
                        commodities.append(entry)
                    else:
                        price_hist.append(entry)


                weather_html     = "".join(f"<li>{e}</li>" for e in weather)     or "<li>No significant impact</li>"
                timing_html      = "".join(f"<li>{e}</li>" for e in timing)      or "<li>No significant impact</li>"
                commodities_html = "".join(f"<li>{e}</li>" for e in commodities) or "<li>No significant impact</li>"
                price_html       = "".join(f"<li>{e}</li>" for e in price_hist)  or "<li>No significant impact</li>"

                st.markdown(f'<div class="section-label">WHY THIS FORECAST · REGIME: {regime_label.upper()}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.1rem; line-height:1.8;">
                    <div style="margin-bottom:1rem;">
                        <div style="font-family:'Space Mono',monospace; font-size:1.0rem; opacity:0.45; letter-spacing:0.12em; margin-bottom:0.4rem;">☀️ WEATHER & SOLAR</div>
                        <ul style="margin:0; padding-left:1.2rem; opacity:0.85;">{weather_html}</ul>
                    </div>
                    <div style="margin-bottom:1rem;">
                        <div style="font-family:'Space Mono',monospace; font-size:1.0rem; opacity:0.45; letter-spacing:0.12em; margin-bottom:0.4rem;">📅 TIMING</div>
                        <ul style="margin:0; padding-left:1.2rem; opacity:0.85;">{timing_html}</ul>
                    </div>
                    <div style="margin-bottom:1rem;">
                        <div style="font-family:'Space Mono',monospace; font-size:1.0rem; opacity:0.45; letter-spacing:0.12em; margin-bottom:0.4rem;">⛽ COMMODITIES</div>
                        <ul style="margin:0; padding-left:1.2rem; opacity:0.85;">{commodities_html}</ul>
                    </div>
                    <div style="margin-bottom:1.5rem;">
                        <div style="font-family:'Space Mono',monospace; font-size:1.0rem; opacity:0.45; letter-spacing:0.12em; margin-bottom:0.4rem;">📈 PRICE HISTORY</div>
                        <ul style="margin:0; padding-left:1.2rem; opacity:0.85;">{price_html}</ul>
                    </div>

                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="opacity:0.3;font-family:Space Mono,monospace;font-size:0.7rem;padding-top:2rem;">Explanation unavailable</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">MARKET INTELLIGENCE · ACTIONABLE INSIGHTS</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <table class="biz-table">
            <thead><tr><th>Indicator</th><th>Value</th><th>Recommendation</th></tr></thead>
            <tbody>
                <tr><td>⚡ Best Charge Window</td>
                    <td class="{'positive' if best_charge_price < 0 else 'warning' if best_charge_price < 20 else ''}">{best_charge_ts} – {best_charge_end} · {best_charge_price:.1f} €/MWh</td>
                    <td>{"⚡ Negative price — grid pays you to charge!" if best_charge_price < 0 else "Optimal 4h battery / pump storage charging window"}</td></tr>
                <tr><td>💰 Best Discharge Window</td>
                    <td class="{'negative' if best_discharge_price > threshold else 'warning' if best_discharge_price > 80 else ''}">{best_discharge_ts} – {best_discharge_end} · {best_discharge_price:.1f} €/MWh</td>
                    <td>{"🔴 Spike window — maximize stored energy revenue" if best_discharge_price > threshold else "Discharge during high demand · maximize revenue"}</td></tr>
                <tr><td>⚠️ Spike Risk</td>
                    <td class="{'negative' if spike_hours > 0 else 'positive'}">{spike_hours}h above {threshold} €/MWh</td>
                    <td>{"Activate hedging contracts or curtailment" if spike_hours > 0 else "No spike risk in window ✓"}</td></tr>
                <tr><td>🟢 Negative Price Hours</td>
                    <td class="{'positive' if neg_hours > 0 else ''}">{neg_hours}h below 0 €/MWh</td>
                    <td>{"Maximize flexible load — grid pays you to consume" if neg_hours > 0 else "No negative prices expected"}</td></tr>
                <tr><td>📊 Price Volatility</td>
                    <td class="{'negative' if std_val > 40 else 'warning' if std_val > 20 else 'positive'}">± {std_val:.1f} €/MWh</td>
                    <td>{"High volatility — active trading recommended" if std_val > 40 else "Moderate volatility — standard hedging sufficient" if std_val > 20 else "Low volatility — stable market conditions"}</td></tr>
                <tr><td>🏭 Industrial Load Scheduling</td>
                    <td class="positive">{best_charge_ts} – {best_charge_end}</td>
                    <td>Schedule energy-intensive operations in cheapest 4h block</td></tr>
                <tr><td>📈 Peak Avoidance Window</td>
                    <td class="negative">{best_discharge_ts} – {best_discharge_end}</td>
                    <td>Reduce consumption · activate demand response</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

# ── BACKTEST VIEW ──────────────────────────────────────────────────────────────
elif view == "Backtest":
    data = st.session_state.backtest_data
    if data and "actual" in data:
        actual     = data["actual"]
        predicted  = data["predicted"]
        timestamps = pd.to_datetime(data["timestamps"], utc=True)
        timestamps_berlin = timestamps.tz_convert('Europe/Berlin')
        df_bt = pd.DataFrame({"timestamp": timestamps_berlin, "actual": actual, "predicted": predicted})

        st.markdown('<div class="section-label">ACTUAL VS PREDICTED · EUROPE/BERLIN</div>', unsafe_allow_html=True)
        fig_bt = go.Figure()
        fig_bt.add_trace(go.Scatter(x=df_bt["timestamp"], y=df_bt["actual"],
            mode="lines", name="Actual", line=dict(color="#378ADD", width=2),
            hovertemplate="<b>Actual</b>: %{y:.1f} €/MWh<extra></extra>"))
        fig_bt.add_trace(go.Scatter(x=df_bt["timestamp"], y=df_bt["predicted"],
            mode="lines", name="Predicted", line=dict(color="#00C49A", width=1.5, dash="dash"),
            hovertemplate="<b>Predicted</b>: %{y:.1f} €/MWh<extra></extra>"))
        fig_bt.update_layout(
            template="plotly_dark", height=450,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", size=10, color="rgba(255,255,255,0.4)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)", tickfont=dict(size=13)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)", tickfont=dict(size=13), ticksuffix=" €"),
            hovermode="x unified", margin=dict(l=50, r=30, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        font=dict(family="Space Mono", size=9), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_bt, use_container_width=True)
    elif data and "error" in data:
        st.error(f"Backtest error: {data.get('message', 'Unknown error')}")

# ── ENERGY MIX VIEW ────────────────────────────────────────────────────────────
elif view == "Energy Mix":
    data = st.session_state.energy_mix_data
    if data:
        timestamps = pd.to_datetime(data["timestamps"], utc=True).tz_convert('Europe/Berlin')
        df_em = pd.DataFrame({
            "timestamp": timestamps,
            "renewable": data["generation_renewable"],
            "non_renewable": data["generation_non_renewable"],
            "consumption": data["consumption"],
        })
        df_em = df_em.dropna(subset=["renewable", "non_renewable"])

        st.markdown('<div class="section-label">ENERGY MIX · RENEWABLE VS NON-RENEWABLE · LAST 7 DAYS</div>', unsafe_allow_html=True)
        fig_em = go.Figure()
        fig_em.add_trace(go.Scatter(
            x=df_em["timestamp"], y=df_em["renewable"],
            mode="lines", name="Renewable", stackgroup='one',
            fillcolor='rgba(0,196,154,0.5)', line=dict(color="#00C49A", width=1),
            hovertemplate="<b>Renewable</b>: %{y:.0f} MW<extra></extra>"))
        fig_em.add_trace(go.Scatter(
            x=df_em["timestamp"], y=df_em["non_renewable"],
            mode="lines", name="Non-Renewable", stackgroup='one',
            fillcolor='rgba(232,69,69,0.4)', line=dict(color="#E84545", width=1),
            hovertemplate="<b>Non-Renewable</b>: %{y:.0f} MW<extra></extra>"))
        fig_em.add_trace(go.Scatter(
            x=df_em["timestamp"], y=df_em["consumption"],
            mode="lines", name="Consumption",
            line=dict(color="#F59E0B", width=2, dash="dot"),
            hovertemplate="<b>Consumption</b>: %{y:.0f} MW<extra></extra>"))
        fig_em.update_layout(
            template="plotly_dark", height=450,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", size=10, color="rgba(255,255,255,0.4)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)", tickfont=dict(size=13)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)", tickfont=dict(size=13), ticksuffix=" MW"),
            hovermode="x unified", margin=dict(l=50, r=30, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        font=dict(family="Space Mono", size=9), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_em, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gi-footer">
    GRID INTELLIGENCE · LE WAGON BERLIN · APRIL 2026 · DE-LU ELECTRICITY MARKET FORECASTING
</div>
""", unsafe_allow_html=True)
