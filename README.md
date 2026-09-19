# ⬡ G10 FX Market Dashboard

> A real-time foreign exchange market monitor covering all G10 currency pairs — built with Python, Streamlit and Plotly. Pulls live data from Yahoo Finance, computes key market metrics, and renders them in a Bloomberg-inspired dark UI you can run locally or deploy for free.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.22%2B-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

---

## What it does

| Panel | Description |
|---|---|
| **Live Quote Strip** | Current price + daily Δ% for all 10 pairs with colour coding |
| **Session Snapshot** | Best/worst performer, highest/lowest vol, avg cross-correlation |
| **Correlation Heatmap** | Rolling pairwise Pearson correlations across the full G10 universe |
| **Realised Volatility** | Configurable rolling annualised vol — multi-line overlay |
| **Daily Range Proxy** | Average High-Low range in pips — free-tier spread/liquidity signal |
| **Cumulative Returns** | Normalised performance for any user-selected subset of pairs |
| **OHLC Candlestick** | Candlestick + Bollinger Bands (20-period) + daily return subplot |
| **Return Distribution** | Log-return histogram overlay per pair |
| **Vol Regime Table** | Multi-horizon vol (5d → 63d) with percentile rank heat colouring |

### Pairs covered

```
EUR/USD  ·  GBP/USD  ·  USD/JPY  ·  USD/CHF  ·  USD/CAD
AUD/USD  ·  NZD/USD  ·  EUR/GBP  ·  EUR/JPY  ·  GBP/JPY
```

---

## Quick Start

```bash
# 1 — clone
git clone https://github.com/ELADMI-jr/fx-dashboard.git
cd fx-dashboard

# 2 — install
pip install -r requirements.txt

# 3 — run
streamlit run app.py
```

Opens at `http://localhost:8501`. No API keys. No paid data feeds.

---

## Sidebar Controls

| Control | Default | Options |
|---|---|---|
| Lookback Period | 90 days | 30 / 60 / 90 / 180 / 252 days |
| Vol Window | 21 days | 5 – 60 days (slider) |
| Chart Pair | EUR/USD | Any G10 pair |
| Multi-Pair Overlay | 4 pairs | Any combination |
| Refresh | — | Force-clears the 5-min cache |

---

## Technical Notes

**Data** — Yahoo Finance via `yfinance`. Daily OHLC, ~15-min delayed on the latest session. No API key required.

**Spread proxy** — True interdealer bid/ask requires a paid feed (Bloomberg, Refinitiv). The dashboard uses the average daily High-Low range in pips, a standard free-tier substitute for effective spread.

**Realised volatility** — Annualised from daily log-returns:

```
σ_ann = std( log(Pₜ / Pₜ₋₁), window=N ) × √252 × 100
```

**Correlations** — Pearson on log-returns over the selected lookback window.

**Pip convention** — JPY crosses (USD/JPY, EUR/JPY, GBP/JPY) use `0.01`; all other pairs use `0.0001`.

**Caching** — `@st.cache_data(ttl=300)` keeps data fresh every 5 minutes without hammering Yahoo Finance.

---

## Project Structure

```
fx-dashboard/
├── app.py            # Streamlit app — single file, ~800 lines
├── requirements.txt  # Python dependencies
├── LICENSE           # MIT
└── README.md
```

---

## Deploy Free on Streamlit Cloud

1. Push this repo to GitHub (already done)
2. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub
3. **New app** → pick `ELADMI-jr/fx-dashboard` → main file `app.py`
4. Hit **Deploy** — live URL in ~2 minutes

No secrets, no environment variables needed.

---

## Roadmap

- [ ] Intraday 15-min candlestick view
- [ ] Interest rate differential overlay (carry signal)
- [ ] VIX / risk-off correlation panel
- [ ] Z-score mean-reversion signal table
- [ ] Pair performance export to CSV

---

## License

MIT © 2025 [Ahmed Eladmi](https://github.com/ELADMI-jr)
