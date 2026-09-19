# ⬡ G10 FX Market Dashboard

> A real-time foreign exchange market monitor covering G10 currency pairs — built with Streamlit and Plotly. Pulls live data from Yahoo Finance, computes key market microstructure metrics, and renders them in a Bloomberg-inspired dark UI.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## Features

| Panel | What it shows |
|-------|---------------|
| **Live Quote Strip** | Current price + daily change for all 10 pairs |
| **Session Snapshot** | Best/worst performer, highest/lowest vol, avg cross-correlation |
| **Correlation Heatmap** | Rolling pairwise correlations across the full G10 universe |
| **Realised Volatility** | Configurable rolling annualised vol (multi-line overlay) |
| **Daily Range Proxy** | Average daily High-Low range in pips — a liquidity/spread signal |
| **Cumulative Returns** | Normalised performance for any subset of pairs |
| **OHLC Candlestick** | Candlestick + Bollinger Bands (20-period) + daily return bars |
| **Return Distribution** | Histogram overlay of log-returns per pair |
| **Vol Regime Table** | Multi-horizon vol (5d → 63d) with percentile rank colouring |

### Pairs covered
`EUR/USD · GBP/USD · USD/JPY · USD/CHF · USD/CAD · AUD/USD · NZD/USD · EUR/GBP · EUR/JPY · GBP/JPY`

---

## Quick Start

```bash
# 1. clone
git clone https://github.com/ahmed-eladmi/fx-dashboard.git
cd fx-dashboard

# 2. install dependencies
pip install -r requirements.txt

# 3. run
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Sidebar Controls

| Control | Default | Description |
|---------|---------|-------------|
| Lookback Period | 90 days | Historical window: 30 / 60 / 90 / 180 / 252 days |
| Vol Window | 21 days | Rolling window for realised volatility |
| Chart Pair | EUR/USD | Pair for the detailed OHLC + Bollinger chart |
| Multi-Pair Overlay | 4 pairs | Subset for cumulative + distribution charts |
| Refresh | — | Force-clears the 5-min data cache |

---

## Technical Notes

**Data source**: Yahoo Finance via `yfinance`. Prices are daily OHLC, delayed ~15 minutes on the most recent session.

**Spread proxy**: True interdealer bid/ask data requires a paid feed (Bloomberg, Refinitiv). As a free-tier substitute, the dashboard computes the average daily High-Low range in pips — a widely accepted proxy for effective spread and liquidity conditions.

**Volatility**: Annualised realised volatility computed from daily log-returns:

```
σ_ann = std(log(P_t / P_{t-1}), window=N) × √252 × 100
```

**Correlations**: Pearson correlation of log-returns over the selected lookback window.

**Pip convention**: JPY pairs (USD/JPY, EUR/JPY, GBP/JPY) use a 0.01 pip value; all others use 0.0001.

---

## Project Structure

```
fx-dashboard/
├── app.py            # Streamlit application (single-file)
├── requirements.txt  # Python dependencies
├── LICENSE           # MIT
└── README.md
```

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select repo, branch `main`, main file `app.py`
4. Deploy — no secrets or API keys required

---

## Roadmap

- [ ] Intraday 15-min candlestick view
- [ ] Interest rate differential overlay (carry trade signal)
- [ ] VIX / risk-off correlation panel
- [ ] Z-score mean-reversion signal table
- [ ] Export to CSV / PDF

---

## License

MIT © 2025 [Ahmed Eladmi](https://github.com/ahmed-eladmi)
