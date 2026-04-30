# Grid Intelligence — Streamlit Hero Background
# 
# Drop-in replacement for the `components.html(...)` video header in app.py.
# Uses your background_grid.png as the centerpiece + animated grid + flow lines
# in YOUR existing palette (Barlow Condensed, #00C49A green, #FF8070 coral).
# 
# USAGE (local test only — do not commit to master):
#   1. Save background_grid.png next to app.py (or in static/)
#   2. Replace the entire `components.html(f"""...""", height=240)` block
#      in app.py with the snippet at the bottom of this file.
#   3. Run streamlit locally: `streamlit run app.py`
# 
# If you prefer to keep the file separate, save the HTML template below
# as `hero_background.html` and load it via:
#   with open("hero_background.html") as f:
#       components.html(f.read().replace("{NOW}", now_str), height=240)

HERO_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Barlow+Condensed:wght@300;400;600;700;900&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: transparent; }

  .gi-hero {
    position: relative;
    width: 100%;
    height: 220px;
    overflow: hidden;
    border-bottom: 2px solid rgba(0,196,154,0.3);
    margin-bottom: 1.5rem;
    border-radius: 8px;
    background:
      radial-gradient(ellipse 70% 90% at 30% 50%, rgba(0,80,60,0.35) 0%, transparent 60%),
      radial-gradient(ellipse 60% 90% at 90% 80%, rgba(80,30,80,0.25) 0%, transparent 55%),
      linear-gradient(180deg, #0a0a0a 0%, #14141c 100%);
  }

  /* Isometric grid floor (drifting) */
  .gi-hero__grid {
    position: absolute;
    inset: -10% -10% -30% -10%;
    background-image:
      linear-gradient(116.57deg, transparent 49.6%, rgba(0,196,154,0.07) 49.8%, rgba(0,196,154,0.07) 50.2%, transparent 50.4%),
      linear-gradient(63.43deg, transparent 49.6%, rgba(0,196,154,0.07) 49.8%, rgba(0,196,154,0.07) 50.2%, transparent 50.4%);
    background-size: 50px 25px, 50px 25px;
    transform: perspective(800px) rotateX(58deg);
    transform-origin: 50% 80%;
    mask-image: linear-gradient(180deg, transparent 0%, black 30%, black 80%, transparent 100%);
    animation: gi-drift 30s linear infinite;
  }
  @keyframes gi-drift {
    0%   { background-position: 0 0, 0 0; }
    100% { background-position: 50px 25px, -50px 25px; }
  }

  /* Brand illustration on the right, breathing */
  .gi-hero__art {
    position: absolute;
    right: 24px;
    top: 50%;
    width: 220px;
    transform: translateY(-50%);
    opacity: 0.55;
    filter: drop-shadow(0 8px 24px rgba(0,196,154,0.25)) hue-rotate(80deg) saturate(0.9);
    animation: gi-breathe 6s ease-in-out infinite;
    pointer-events: none;
  }
  .gi-hero__art img { width: 100%; height: auto; display: block; }
  @keyframes gi-breathe {
    0%, 100% { transform: translateY(-50%) scale(1); }
    50%      { transform: translateY(-51%) scale(1.02); }
  }

  /* Current-flow lines (green pulses) */
  .gi-hero__flow { position: absolute; inset: 0; pointer-events: none; }
  .gi-hero__flow path {
    fill: none;
    stroke: url(#gi-flow-gradient);
    stroke-width: 1.5;
    stroke-linecap: round;
    stroke-dasharray: 4 200;
    animation: gi-flow 5s linear infinite;
  }
  .gi-hero__flow path:nth-child(2) { animation-delay: -1.5s; animation-duration: 7s; }
  .gi-hero__flow path:nth-child(3) { animation-delay: -3s; animation-duration: 6s; }
  .gi-hero__flow path:nth-child(4) { animation-delay: -2.2s; animation-duration: 8s; }
  @keyframes gi-flow {
    0%   { stroke-dashoffset: 0; }
    100% { stroke-dashoffset: -204; }
  }

  /* Glowing nodes flickering like the tower lights */
  .gi-hero__node {
    position: absolute;
    width: 5px; height: 5px;
    border-radius: 99px;
    background: #00C49A;
    box-shadow: 0 0 6px #00C49A, 0 0 16px rgba(0,196,154,0.6), 0 0 32px rgba(0,196,154,0.3);
    animation: gi-flicker 3s ease-in-out infinite;
  }
  .gi-hero__node--coral {
    background: #FF8070;
    box-shadow: 0 0 6px #FF8070, 0 0 16px rgba(255,128,112,0.6), 0 0 32px rgba(255,100,80,0.3);
  }
  @keyframes gi-flicker {
    0%, 100% { opacity: 0.4; transform: scale(0.9); }
    45%      { opacity: 1;   transform: scale(1.1); }
  }

  /* Left-side gradient overlay so text stays readable */
  .gi-hero__overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to right,
      rgba(0,0,0,0.85) 0%,
      rgba(0,0,0,0.5) 50%,
      rgba(0,0,0,0.1) 100%);
    z-index: 1;
  }

  .gi-hero__content {
    position: relative;
    z-index: 2;
    padding: 1.8rem 2rem 1.4rem 2rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .gi-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #fff;
    line-height: 1;
    margin: 0;
  }
  .gi-title span { color: #00C49A; }
  .gi-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.55);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 0.4rem;
  }
  .gi-badges { margin-top: 1rem; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .gi-badge {
    display: inline-block;
    background: rgba(0,196,154,0.12);
    border: 1px solid rgba(0,196,154,0.35);
    color: #00C49A;
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.1em;
    padding: 3px 10px;
    border-radius: 3px;
    text-transform: uppercase;
  }
  .gi-badge-red {
    background: rgba(255,100,80,0.12);
    border-color: rgba(255,100,80,0.35);
    color: #FF8070;
  }
  .status-live {
    display: inline-block;
    width: 7px; height: 7px;
    background: #00C49A;
    border-radius: 50%;
    margin-right: 5px;
    animation: pulse 2s infinite;
  }
  .live-text {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    color: rgba(255,255,255,0.4);
    margin-left: 4px;
  }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }
</style>
</head>
<body>
<div class="gi-hero">
  <div class="gi-hero__grid"></div>

  <div class="gi-hero__art">
    <img src="BACKGROUND_PNG_URL" alt="" />
  </div>

  <svg class="gi-hero__flow" viewBox="0 0 1200 220" preserveAspectRatio="xMidYMid slice">
    <defs>
      <linearGradient id="gi-flow-gradient" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0%"  stop-color="#00C49A" stop-opacity="0"/>
        <stop offset="50%" stop-color="#00C49A" stop-opacity="1"/>
        <stop offset="100%" stop-color="#00C49A" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <path d="M -50 60 Q 300 40, 600 80 T 1250 60" />
    <path d="M -50 130 Q 300 110, 600 150 T 1250 130" />
    <path d="M -50 180 Q 400 160, 800 200 T 1250 180" />
    <path d="M -50 100 Q 500 130, 900 90 T 1250 110" />
  </svg>

  <span class="gi-hero__node" style="left: 8%;  top: 30%; animation-delay: -0.3s;"></span>
  <span class="gi-hero__node gi-hero__node--coral" style="left: 18%; top: 70%; animation-delay: -1.2s;"></span>
  <span class="gi-hero__node" style="left: 42%; top: 22%; animation-delay: -2.1s;"></span>
  <span class="gi-hero__node gi-hero__node--coral" style="left: 58%; top: 78%; animation-delay: -0.8s;"></span>
  <span class="gi-hero__node" style="left: 72%; top: 35%; animation-delay: -1.6s;"></span>
  <span class="gi-hero__node" style="left: 86%; top: 60%; animation-delay: -2.4s;"></span>

  <div class="gi-hero__overlay"></div>

  <div class="gi-hero__content">
    <p class="gi-title">⚡ Grid<span>Intelligence</span></p>
    <p class="gi-subtitle">Day-Ahead Electricity Price Forecasting · DE-LU Bidding Zone</p>
    <div class="gi-badges">
      <span class="gi-badge">Multi-Regime XGBoost</span>
      <span class="gi-badge">72h · 15min Resolution</span>
      <span class="gi-badge gi-badge-red">ENTSO-E · Open-Meteo · TTF</span>
      <span class="live-text"><span class="status-live"></span>LIVE · {NOW}</span>
    </div>
  </div>
</div>
</body>
</html>
"""

# ============================================================================
# DROP-IN SNIPPET FOR app.py
# ============================================================================
# Replace the entire `components.html(f"""<video...>""", height=240)` block
# (lines ~258-330 in your app.py) with this:
#
# import base64, pathlib
# 
# # Embed the PNG as base64 so it works locally and in Streamlit Cloud
# _png_path = pathlib.Path(__file__).parent / "background_grid.png"
# _png_b64  = base64.b64encode(_png_path.read_bytes()).decode()
# _png_url  = f"data:image/png;base64,{_png_b64}"
# 
# now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
# 
# components.html(
#     HERO_HTML
#       .replace("BACKGROUND_PNG_URL", _png_url)
#       .replace("{NOW}", now_str),
#     height=240,
# )
#
# ============================================================================
