import os
import base64
import pathlib
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
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

# ── Background icon (base64) ──────────────────────────────────────────────────
_png_path = pathlib.Path(__file__).parent / "background_grid.png"
if _png_path.exists():
    _png_b64 = base64.b64encode(_png_path.read_bytes()).decode()
    _png_url = f"data:image/png;base64,{_png_b64}"
else:
    _png_url = ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Barlow+Condensed:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] {{ font-family: 'Barlow Condensed', sans-serif; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; position: relative; z-index: 1; }}

/* ── Page-corner background icon (bottom-right only) ────────────────── */
.stApp::before {{
    content: "";
    position: fixed;
    right: -120px;
    bottom: -100px;
    width: 520px;
    height: 520px;
    background-image: url("{_png_url}");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: bottom right;
    opacity: 0.10;
    filter: hue-rotate(80deg) saturate(1.5);
    pointer-events: none;
    z-index: 0;
}}
.stApp::after {{
    content: "";
    position: fixed;
    right: -180px;
    top: -60px;
    width: 480px;
    height: 480px;
    background-image: url("{_png_url}");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: top right;
    opacity: 0.02;
    filter: hue-rotate(80deg) saturate(0.8);
    pointer-events: none;
    z-index: 0;
    transform: scaleX(-1);
}}

/* ── Metric card ─────────────────────────────────────────────────── */
.metric-card {{
    background: #171717;
    border: 1px solid rgba(255,255,255,0.1);
    border-top: 3px solid #00C49A;
    border-radius: 6px; padding: 1.2rem 1.3rem;
    min-height: 170px;
    position: relative;
    z-index: 1;
}}
.metric-card.danger  {{ border-top-color: #E84545; }}
.metric-card.warning {{ border-top-color: #F59E0B; }}
.metric-card.neutral {{ border-top-color: rgba(255,255,255,0.2); }}

/* ── Generic box (chart + shap wrappers, same look as metric-card) ── */
.box {{
    background: #171717;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    padding: 1.2rem 1.3rem;
    position: relative;
    z-index: 1;
    margin-bottom: 1rem;
}}
.box--accent {{ border-top: 3px solid #00C49A; }}
.box--coral  {{ border-top: 3px solid #FF8070; }}
.box__title {{
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.55);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin: 0 0 1rem 0;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.box__title span {{
    float: right;
    color: rgba(255,255,255,0.35);
    font-size: 0.62rem;
    letter-spacing: 0.12em;
}}

/* Auto-wrap any plotly chart in a box look (fully opaque) */
div[data-testid="stPlotlyChart"] {{
    background: #171717;
    border: 1px solid #2a2a2a;
    border-top: 3px solid #00C49A;
    border-radius: 6px;
    padding: 1rem;
    position: relative;
    z-index: 1;
}}
.metric-icon {{ width: 28px; height: 28px; margin-bottom: 10px; }}
.metric-label {{
    font-family: 'Space Mono', monospace; font-size: 0.6rem;
    color: var(--text-color); opacity: 0.45;
    letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 4px;
}}
.metric-value {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.4rem; font-weight: 700;
    color: var(--text-color); line-height: 1;
}}
.metric-unit {{ font-size: 1.1rem; color: var(--text-color); opacity: 0.45; font-weight: 400; }}
.metric-sub {{
    font-family: 'Space Mono', monospace; font-size: 1.0rem;
    color: var(--text-color); opacity: 0.45; margin-top: 6px;
}}

.section-label {{
    font-family: 'Space Mono', monospace; font-size: 1.0rem;
    color: var(--text-color); opacity: 0.4;
    letter-spacing: 0.18em; text-transform: uppercase;
    border-left: 3px solid #00C49A; padding-left: 8px; margin-bottom: 1rem;
    position: relative; z-index: 1;
}}

.biz-table {{
    width: 100%; border-collapse: collapse;
    background: #171717;
    border: 1px solid #2a2a2a;
    border-top: 3px solid #00C49A;
    border-radius: 6px; overflow: hidden;
    font-family: 'Barlow Condensed', sans-serif;
    position: relative; z-index: 1;
}}
.biz-table thead tr {{ background: #1f1f1f; }}
.biz-table thead th {{
    font-family: 'Space Mono', monospace; font-size: 1.0rem;
    letter-spacing: 0.14em; text-transform: uppercase;
    padding: 10px 16px; text-align: left; font-weight: 400;
    color: var(--text-color); opacity: 0.4;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}}
.biz-table tbody tr {{ border-bottom: 1px solid rgba(255,255,255,0.05); }}
.biz-table tbody tr:last-child {{ border-bottom: none; }}
.biz-table tbody tr:hover {{ background: rgba(255,255,255,0.04); }}
.biz-table td {{ padding: 11px 16px; font-size: 1.2rem; color: var(--text-color); vertical-align: middle; }}
.biz-table td:first-child {{ font-size: 1.2rem; color: var(--text-color); opacity: 0.55; width: 28%; }}
.biz-table td:nth-child(2) {{ font-weight: 600; width: 30%; }}
.biz-table td.positive {{ color: #00C49A !important; opacity: 1; }}
.biz-table td.negative {{ color: #E84545 !important; opacity: 1; }}
.biz-table td.warning  {{ color: #F59E0B !important; opacity: 1; }}

.stSelectbox label {{
    color: var(--text-color) !important; opacity: 0.5;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.58rem !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}}

.gi-footer {{
    font-family: 'Space Mono', monospace; font-size: 1.0rem;
    color: var(--text-color); opacity: 0.2; text-align: center;
    padding: 2rem 0 1rem 0; letter-spacing: 0.1em;
    border-top: 1px solid rgba(255,255,255,0.08); margin-top: 2rem;
    position: relative; z-index: 1;
}}
</style>
""", unsafe_allow_html=True)

# ── Business Labels for SHAP Features ─────────────────────────────────────────
FEATURE_LABELS = {
    "price_lag_1": "Price 15 min ago", "price_lag_4": "Price 1h ago",
    "price_lag_12": "Price 3h ago", "price_lag_24": "Price 6h ago",
    "price_lag_96": "Price 24h ago", "price_lag_672": "Price 1 week ago",
    "price_roll_mean_24": "Avg Price last 6h", "price_roll_mean_96": "Avg Price last 24h",
    "price_roll_mean_672": "Avg Price last week", "price_roll_std_4": "Price Volatility 1h",
    "price_roll_std_96": "Price Volatility 24h",
    "generation_renewable": "Renewable Generation",
    "generation_non_renewable": "Conventional Generation",
    "consumption": "Power Consumption",
    "wind_onshore": "Onshore Wind Power", "wind_speed_ms_observed": "Wind Speed",
    "temperature_c_observed": "Temperature",
    "shortwave_radiation_wm2_observed": "Solar Radiation",
    "cloud_cover_percent_observed": "Cloud Cover",
    "wti_oil": "WTI Oil Price", "natural_gas": "Natural Gas Price", "ttf_gas": "TTF Gas Price",
    "hour": "Time of Day", "day_of_week": "Day of Week", "day_of_year": "Season",
    "month": "Month", "renewable_ratio": "Renewable Share in Mix",
}

ICON_DOWN = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="#00C49A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>"""
ICON_UP = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="#E84545" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>"""
ICON_AVG = """<svg class="metric-icon" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="22" y1="12" x2="2" y2="12"/>
  <path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/></svg>"""

now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

# ── Hero (animated, ORIGINAL) ─────────────────────────────────────────────────
HERO_HTML = """<!DOCTYPE html>
<html><head><style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Barlow+Condensed:wght@300;400;600;700;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0}body{background:transparent}
.gi-hero{position:relative;width:100%;height:220px;overflow:hidden;border-bottom:2px solid rgba(0,196,154,0.3);margin-bottom:1.5rem;border-radius:8px;background:radial-gradient(ellipse 70% 90% at 30% 50%,rgba(0,80,60,0.35) 0%,transparent 60%),radial-gradient(ellipse 60% 90% at 90% 80%,rgba(80,30,80,0.25) 0%,transparent 55%),linear-gradient(180deg,#0a0a0a 0%,#14141c 100%)}
.gi-hero__grid{position:absolute;inset:-10% -10% -30% -10%;background-image:linear-gradient(116.57deg,transparent 49.6%,rgba(0,196,154,0.07) 49.8%,rgba(0,196,154,0.07) 50.2%,transparent 50.4%),linear-gradient(63.43deg,transparent 49.6%,rgba(0,196,154,0.07) 49.8%,rgba(0,196,154,0.07) 50.2%,transparent 50.4%);background-size:50px 25px,50px 25px;transform:perspective(800px) rotateX(58deg);transform-origin:50% 80%;mask-image:linear-gradient(180deg,transparent 0%,black 30%,black 80%,transparent 100%);animation:gi-drift 30s linear infinite}
@keyframes gi-drift{0%{background-position:0 0,0 0}100%{background-position:50px 25px,-50px 25px}}
.gi-hero__art{position:absolute;right:24px;top:50%;width:240px;transform:translateY(-50%);opacity:0.5;filter:drop-shadow(0 8px 24px rgba(0,196,154,0.35));animation:gi-breathe 6s ease-in-out infinite;pointer-events:none;z-index:1}
.gi-hero__art img{width:100%;display:block}
@keyframes gi-breathe{0%,100%{transform:translateY(-50%) scale(1)}50%{transform:translateY(-51%) scale(1.02)}}
.gi-hero__flow{position:absolute;inset:0;pointer-events:none}
.gi-hero__flow path{fill:none;stroke:url(#flowg);stroke-width:1.5;stroke-linecap:round;stroke-dasharray:4 200;animation:gi-flow 5s linear infinite}
.gi-hero__flow path:nth-child(2){animation-delay:-1.5s;animation-duration:7s}
.gi-hero__flow path:nth-child(3){animation-delay:-3s;animation-duration:6s}
.gi-hero__flow path:nth-child(4){animation-delay:-2.2s;animation-duration:8s}
@keyframes gi-flow{0%{stroke-dashoffset:0}100%{stroke-dashoffset:-204}}
.gi-hero__node{position:absolute;width:5px;height:5px;border-radius:99px;background:#00C49A;box-shadow:0 0 6px #00C49A,0 0 16px rgba(0,196,154,0.6),0 0 32px rgba(0,196,154,0.3);animation:gi-flicker 3s ease-in-out infinite}
.gi-hero__node--coral{background:#FF8070;box-shadow:0 0 6px #FF8070,0 0 16px rgba(255,128,112,0.6)}
@keyframes gi-flicker{0%,100%{opacity:0.4;transform:scale(0.9)}45%{opacity:1;transform:scale(1.1)}}
.gi-hero__overlay{position:absolute;inset:0;background:linear-gradient(to right,rgba(0,0,0,0.85) 0%,rgba(0,0,0,0.5) 50%,rgba(0,0,0,0.1) 100%);z-index:1}
.gi-hero__content{position:relative;z-index:2;padding:1.8rem 2rem;height:100%;display:flex;flex-direction:column;justify-content:center}
.gi-title{font-family:'Barlow Condensed',sans-serif;font-size:2rem;font-weight:900;letter-spacing:0.06em;text-transform:uppercase;color:#fff;line-height:1}
.gi-title span{color:#00C49A}
.gi-subtitle{font-family:'Space Mono',monospace;font-size:0.72rem;color:rgba(255,255,255,0.55);letter-spacing:0.14em;text-transform:uppercase;margin-top:0.4rem}
.gi-badges{margin-top:1rem;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.gi-badge{background:rgba(0,196,154,0.12);border:1px solid rgba(0,196,154,0.35);color:#00C49A;font-family:'Space Mono',monospace;font-size:0.58rem;letter-spacing:0.1em;padding:3px 10px;border-radius:3px;text-transform:uppercase}
.gi-badge-red{background:rgba(255,100,80,0.12);border-color:rgba(255,100,80,0.35);color:#FF8070}
.status-live{display:inline-block;width:7px;height:7px;background:#00C49A;border-radius:50%;margin-right:5px;animation:pulse 2s infinite}
.live-text{font-family:'Space Mono',monospace;font-size:0.58rem;color:rgba(255,255,255,0.4);margin-left:4px}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.2}}
</style></head><body>
<div class="gi-hero">
  <div class="gi-hero__grid"></div>
  <div class="gi-hero__art"><img src="BACKGROUND_PNG_URL" alt=""/></div>
  <svg class="gi-hero__flow" viewBox="0 0 1200 220" preserveAspectRatio="xMidYMid slice">
    <defs><linearGradient id="flowg" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#00C49A" stop-opacity="0"/>
      <stop offset="50%" stop-color="#00C49A" stop-opacity="1"/>
      <stop offset="100%" stop-color="#00C49A" stop-opacity="0"/>
    </linearGradient></defs>
    <path d="M -50 60 Q 300 40, 600 80 T 1250 60"/>
    <path d="M -50 130 Q 300 110, 600 150 T 1250 130"/>
    <path d="M -50 180 Q 400 160, 800 200 T 1250 180"/>
    <path d="M -50 100 Q 500 130, 900 90 T 1250 110"/>
  </svg>
  <span class="gi-hero__node" style="left:8%;top:30%;animation-delay:-0.3s;"></span>
  <span class="gi-hero__node gi-hero__node--coral" style="left:18%;top:70%;animation-delay:-1.2s;"></span>
  <span class="gi-hero__node" style="left:42%;top:22%;animation-delay:-2.1s;"></span>
  <span class="gi-hero__node gi-hero__node--coral" style="left:58%;top:78%;animation-delay:-0.8s;"></span>
  <span class="gi-hero__node" style="left:72%;top:35%;animation-delay:-1.6s;"></span>
  <span class="gi-hero__node" style="left:86%;top:60%;animation-delay:-2.4s;"></span>
  <div class="gi-hero__overlay"></div>
  <div class="gi-hero__content">
    <p class="gi-title">⚡ Grid<span>Intelligence</span></p>
    <p class="gi-subtitle">Day-Ahead Electricity Price Forecasting · DE-LU Bidding Zone</p>
    <div class="gi-badges">
      <span class="gi-badge">Multi-Regime XGBoost</span>
      <span class="gi-badge">72h · 15min Resolution</span>
      <span class="gi-badge gi-badge-red">ENTSO-E · Open-Meteo · TTF</span>
      <span class="live-text"><span class="status-live"></span>LIVE · __NOW__</span>
    </div>
  </div>
</div>
</body></html>"""

components.html(
    HERO_HTML.replace("BACKGROUND_PNG_URL", _png_url).replace("__NOW__", now_str),
    height=240,
)

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in [
    ("prediction_data", None), ("backtest_data", None), ("backtest_days", 7),
    ("energy_mix_data", None), ("explain_data", None)
]:
    if key not in st.session_state:
        st.session_state[key] = val


# ── Cache functions ────────────────────────────────────────────────────────────
@st.cache_data(ttl=900)
def fetch_predictions():
    r = requests.get(BASE_URI + '/predict', timeout=60)
    return r.json()

@st.cache_data(ttl=900)
def fetch_explain():
    r = requests.get(BASE_URI + '/explain', timeout=60)
    return r.json()

@st.cache_data(ttl=900)
def fetch_backtest(days):
    r = requests.get(BASE_URI + f'/backtest?days={days}', timeout=60)
    return r.json()

@st.cache_data(ttl=900)
def fetch_energy_mix():
    r = requests.get(BASE_URI + '/energy-mix?days=7', timeout=60)
    return r.json()

# ── Controls ──────────────────────────────────────────────────────────────────
col_view, col_days, _ = st.columns([2, 2, 6])
with col_view:
    view = st.selectbox("VIEW", options=["Predict next 72 hours", "Backtest", "Energy Mix"], index=0)
with col_days:
    if view == "Backtest":
        days = st.selectbox("BACKTEST WINDOW", options=[1, 3, 7, 14], index=3)
        if days != st.session_state.backtest_days:   # ← adentro del if
            st.session_state.backtest_days = days



# ── Fetch ──────────────────────────────────────────────────────────────────────
if view == "Predict next 72 hours":
    with st.spinner("⚡ Loading forecast..."):
        try:
            st.session_state.prediction_data = fetch_predictions()
        except Exception as e:
            st.error(f"API connection failed: {e}")
    with st.spinner("Computing SHAP explanations..."):
        try:
            st.session_state.explain_data = fetch_explain()
        except Exception as e:
            st.warning(f"SHAP explanation unavailable: {e}")

# ── Prefetch all views on first load ──────────────────────────────────────────
if "prefetched" not in st.session_state:
    try:
        st.session_state.prediction_data = fetch_predictions()
        st.session_state.explain_data = fetch_explain()
        st.session_state.backtest_data = fetch_backtest(14)  # ← siempre 14 días
        st.session_state.energy_mix_data = fetch_energy_mix()
    except Exception:
        pass
    st.session_state.prefetched = True

# ── PREDICT VIEW ───────────────────────────────────────────────────────────────
if view == "Predict next 72 hours":
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=60_000, key="now_line_refresh")
    except ImportError:
        pass

    data = st.session_state.prediction_data
    if data:
        predictions = data["predictions_15min"]
        timestamps  = pd.to_datetime(data["timestamps"], utc=True).tz_convert('Europe/Berlin')
        df = pd.DataFrame({"timestamp": timestamps, "price": predictions})
        threshold = 140

        min_val = min(predictions); max_val = max(predictions)
        avg_val = sum(predictions) / len(predictions)
        std_val = float(np.std(predictions))
        spike_hours = sum(1 for p in predictions if p > threshold) // 4
        neg_hours   = sum(1 for p in predictions if p < 0) // 4
        min_ts = timestamps[predictions.index(min_val)].strftime("%a %d %b %H:%M")
        max_ts = timestamps[predictions.index(max_val)].strftime("%a %d %b %H:%M")

        window = 16
        bcs = int(np.argmin([sum(predictions[i:i+window]) for i in range(len(predictions)-window)]))
        bcs_ts = timestamps[bcs].strftime("%a %d %b %H:%M")
        bcs_end = timestamps[min(bcs+window, len(timestamps)-1)].strftime("%H:%M")
        bcs_p = predictions[bcs]

        window2 = 8
        bds = int(np.argmax([sum(predictions[i:i+window2]) for i in range(len(predictions)-window2)]))
        bds_ts = timestamps[bds].strftime("%a %d %b %H:%M")
        bds_end = timestamps[min(bds+window2, len(timestamps)-1)].strftime("%H:%M")
        bds_p = predictions[bds]

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
            if avg_val < 100:
                dot_color = "#00C49A"; action_text = "Charge Now"
                action_sub = f"Avg {avg_val:.0f} €/MWh · cheap window"; card_class = ""
            elif avg_val <= 200:
                dot_color = "#F59E0B"; action_text = "Neutral · Monitor"
                action_sub = f"Avg {avg_val:.0f} €/MWh · normal range"; card_class = "warning"
            else:
                dot_color = "#E84545"; action_text = "Reduce Load"
                action_sub = f"Avg {avg_val:.0f} €/MWh · high risk"; card_class = "danger"

            st.markdown(f"""
            <style>
            @keyframes outlook-pulse {{
                0%, 100% {{ box-shadow: 0 0 0 0 {dot_color}66; transform: scale(1); }}
                50% {{ box-shadow: 0 0 0 8px {dot_color}00; transform: scale(1.15); }}
            }}
            </style>
            <div class="metric-card {card_class}">
                <div class="metric-label">Market Outlook</div>
                <div style="display:flex; align-items:center; gap:10px; margin-top:0.6rem;">
                    <div style="width:12px;height:12px;border-radius:50%;background:{dot_color};flex-shrink:0;animation:outlook-pulse 2s infinite;"></div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.8rem;font-weight:700;line-height:1;color:{dot_color};">
                        {action_text}
                    </div>
                </div>
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;opacity:0.4;margin-top:0.5rem;letter-spacing:0.08em;">
                    {action_sub}
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

        # Pre-compute regime label so we can place both section-labels at the same height
        explain_pre = st.session_state.get("explain_data")
        regime_map = {0: "Normal", 1: "Positive Spike", 2: "Negative Spike"}
        regime_label_top = regime_map.get(explain_pre.get("regime", 0), "Normal") if explain_pre else "—"

        lbl_chart, _lbl_sp, lbl_shap = st.columns([4, 0.3, 2])
        with lbl_chart:
            st.markdown('<div class="section-label">PRICE FORECAST · 15-MIN INTERVALS · EUROPE/BERLIN</div>', unsafe_allow_html=True)
        with lbl_shap:
            st.markdown(f'<div class="section-label">WHY THIS FORECAST · REGIME: {regime_label_top.upper()}</div>', unsafe_allow_html=True)

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
            now_berlin = pd.Timestamp.now(tz='Europe/Berlin')
            fig.add_vline(x=now_berlin.timestamp()*1000,
                line_color="rgba(56,138,221,0.9)", line_width=2, line_dash="solid",
                annotation_text="NOW", annotation_position="top",
                annotation_font_color="rgba(56,138,221,0.9)", annotation_font_size=9)
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
                regime_label = regime_map.get(explain.get("regime", 0), "Normal")

                weather, timing, commodities, price_hist = [], [], [], []
                seen_base = set()

                for f in features:
                    name = f["feature"]; val = f["shap_value"]
                    base = name.split("_lag_")[0].split("_roll_")[0]
                    if base in seen_base: continue
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

                st.markdown(f"""
                <div class="box" style="border-top:3px solid #00C49A;">
                <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.1rem; line-height:1.8; position:relative; z-index:1;">
                    <div style="margin-bottom:1rem;">
                        <div style="font-family:'Space Mono',monospace; font-size:1.0rem; opacity:0.45; letter-spacing:0.12em; margin-bottom:0.4rem;">☀️ WEATHER &amp; SOLAR</div>
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
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="box" style="border-top:3px solid rgba(255,255,255,0.2);opacity:0.5;font-family:Space Mono,monospace;font-size:0.7rem;">Explanation unavailable</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">MARKET INTELLIGENCE · ACTIONABLE INSIGHTS</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <table class="biz-table">
            <thead><tr><th>Indicator</th><th>Value</th><th>Recommendation</th></tr></thead>
            <tbody>
                <tr><td>⚡ Best Charge Window</td>
                    <td class="{'positive' if bcs_p < 0 else 'warning' if bcs_p < 20 else ''}">{bcs_ts} – {bcs_end} · {bcs_p:.1f} €/MWh</td>
                    <td>{"⚡ Negative price — grid pays you to charge!" if bcs_p < 0 else "Optimal 4h battery / pump storage charging window"}</td></tr>
                <tr><td>💰 Best Discharge Window</td>
                    <td class="{'negative' if bds_p > threshold else 'warning' if bds_p > 80 else ''}">{bds_ts} – {bds_end} · {bds_p:.1f} €/MWh</td>
                    <td>{"🔴 Spike window — maximize stored energy revenue" if bds_p > threshold else "Discharge during high demand · maximize revenue"}</td></tr>
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
                    <td class="positive">{bcs_ts} – {bcs_end}</td>
                    <td>Schedule energy-intensive operations in cheapest 4h block</td></tr>
                <tr><td>📈 Peak Avoidance Window</td>
                    <td class="negative">{bds_ts} – {bds_end}</td>
                    <td>Reduce consumption · activate demand response</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

# ── BACKTEST VIEW ──────────────────────────────────────────────────────────────
elif view == "Backtest":
    data = st.session_state.backtest_data
    if data and "actual" in data:
        timestamps = pd.to_datetime(data["timestamps"], utc=True).tz_convert('Europe/Berlin')
        df_bt = pd.DataFrame({"timestamp": timestamps, "actual": data["actual"], "predicted": data["predicted"]})

        # Filtrar localmente según días seleccionados — sin llamar al backend
        cutoff = df_bt["timestamp"].max() - pd.Timedelta(days=st.session_state.backtest_days)
        df_bt = df_bt[df_bt["timestamp"] >= cutoff]

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
        }).dropna(subset=["renewable", "non_renewable"])

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
