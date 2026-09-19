"""
FX Market Dashboard — G10 Pairs
Author : Ahmed Eladmi
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FX Dashboard · G10",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colour palette ────────────────────────────────────────────────────────────
BG        = "#0d1117"
SURFACE   = "#161b22"
BORDER    = "#30363d"
TEXT      = "#e6edf3"
MUTED     = "#8b949e"
GREEN     = "#3fb950"
RED       = "#f85149"
BLUE      = "#58a6ff"
YELLOW    = "#d29922"
PURPLE    = "#bc8cff"
ORANGE    = "#ffa657"

PAIR_COLOURS = {
    "EURUSD": "#58a6ff",
    "GBPUSD": "#3fb950",
    "USDJPY": "#ffa657",
    "USDCHF": "#bc8cff",
    "USDCAD": "#d29922",
    "AUDUSD": "#39d353",
    "NZDUSD": "#f78166",
    "EURGBP": "#79c0ff",
    "EURJPY": "#ffb77a",
    "GBPJPY": "#a371f7",
}

# ── CSS injection ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* ── global ── */
  .stApp {{ background-color: {BG}; color: {TEXT}; }}
  section[data-testid="stSidebar"] {{ background-color: {SURFACE}; border-right: 1px solid {BORDER}; }}
  .block-container {{ padding-top: 1rem; padding-bottom: 1rem; }}

  /* ── metric tiles ── */
  div[data-testid="metric-container"] {{
      background: {SURFACE};
      border: 1px solid {BORDER};
      border-radius: 8px;
      padding: 12px 16px;
  }}
  div[data-testid="metric-container"] label {{ color: {MUTED} !important; font-size: 11px !important; letter-spacing: .06em; text-transform: uppercase; }}
  div[data-testid="metric-container"] div[data-testid="metric-value"] {{ font-size: 22px !important; font-weight: 600; color: {TEXT}; }}

  /* ── header strip ── */
  .header-strip {{
      background: {SURFACE};
      border: 1px solid {BORDER};
      border-radius: 8px;
      padding: 14px 20px;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
  }}
  .header-title {{
      font-size: 22px;
      font-weight: 700;
      color: {TEXT};
      letter-spacing: -.3px;
  }}
  .header-sub {{
      font-size: 12px;
      color: {MUTED};
      margin-top: 2px;
  }}
  .badge {{
      background: {BORDER};
      color: {MUTED};
      border-radius: 12px;
      padding: 2px 10px;
      font-size: 11px;
      font-weight: 500;
      letter-spacing: .04em;
  }}
  .live-dot {{
      width: 8px; height: 8px;
      background: {GREEN};
      border-radius: 50%;
      display: inline-block;
      margin-right: 5px;
      animation: pulse 2s infinite;
  }}
  @keyframes pulse {{
      0%   {{ opacity: 1; }}
      50%  {{ opacity: .3; }}
      100% {{ opacity: 1; }}
  }}

  /* ── section labels ── */
  .section-label {{
      font-size: 11px;
      font-weight: 600;
      color: {MUTED};
      text-transform: uppercase;
      letter-spacing: .1em;
      margin-bottom: 8px;
      padding-bottom: 6px;
      border-bottom: 1px solid {BORDER};
  }}

  /* ── quote cards ── */
  .quote-card {{
      background: {SURFACE};
      border: 1px solid {BORDER};
      border-radius: 8px;
      padding: 10px 14px;
      text-align: center;
  }}
  .quote-pair  {{ font-size: 11px; font-weight: 600; color: {MUTED}; letter-spacing:.08em; }}
  .quote-price {{ font-size: 20px; font-weight: 700; color: {TEXT}; font-variant-numeric: tabular-nums; }}
  .quote-chg   {{ font-size: 12px; font-weight: 500; margin-top: 2px; }}
  .pos {{ color: {GREEN}; }}
  .neg {{ color: {RED};   }}

  /* ── plotly chart frames ── */
  .chart-frame {{
      background: {SURFACE};
      border: 1px solid {BORDER};
      border-radius: 8px;
      padding: 6px;
      margin-bottom: 12px;
  }}

  /* ── sidebar ── */
  .sidebar-section {{ margin-bottom: 20px; }}
  div[data-baseweb="select"] > div {{ background-color: {BORDER} !important; border-color: {BORDER} !important; }}
  .stSlider [data-testid="stTickBar"] {{ display:none; }}

  /* hide streamlit chrome ── */
  #MainMenu {{ visibility: hidden; }}
  footer     {{ visibility: hidden; }}
  header     {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── constants ─────────────────────────────────────────────────────────────────
G10_PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "USD/CHF": "USDCHF=X",
    "USD/CAD": "USDCAD=X",
    "AUD/USD": "AUDUSD=X",
    "NZD/USD": "NZDUSD=X",
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
}

PAIR_LABELS   = list(G10_PAIRS.keys())
PAIR_TICKERS  = list(G10_PAIRS.values())
SHORT_LABELS  = [p.replace("/", "") for p in PAIR_LABELS]

JPY_PAIRS     = {"USDJPY=X", "EURJPY=X", "GBPJPY=X"}

PLOTLY_LAYOUT = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=BG,
    font=dict(family="Inter, sans-serif", color=TEXT, size=12),
    margin=dict(l=12, r=12, t=36, b=12),
    xaxis=dict(gridcolor=BORDER, showgrid=True, zeroline=False,
               tickfont=dict(color=MUTED, size=10)),
    yaxis=dict(gridcolor=BORDER, showgrid=True, zeroline=False,
               tickfont=dict(color=MUTED, size=10)),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER,
                borderwidth=0, font=dict(size=10, color=MUTED)),
    hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER,
                    font=dict(color=TEXT, size=11)),
)

# ── data layer ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_fx(lookback_days: int) -> pd.DataFrame:
    end   = datetime.utcnow()
    start = end - timedelta(days=lookback_days + 5)
    raw   = yf.download(
        PAIR_TICKERS,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=True,
        progress=False,
    )
    close = raw["Close"].copy()
    close.columns = SHORT_LABELS
    close.dropna(how="all", inplace=True)
    close.ffill(inplace=True)
    return close.tail(lookback_days)


@st.cache_data(ttl=60, show_spinner=False)
def fetch_intraday(ticker: str) -> pd.DataFrame:
    raw = yf.download(ticker, period="5d", interval="15m",
                      auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame()
    df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df.dropna(inplace=True)
    return df


def pip_value(ticker: str) -> float:
    return 0.01 if ticker in JPY_PAIRS else 0.0001


def compute_metrics(close: pd.DataFrame, vol_window: int) -> dict:
    log_ret = np.log(close / close.shift(1)).dropna()

    # rolling annualised realised vol (%)
    ann_vol = log_ret.rolling(vol_window).std() * np.sqrt(252) * 100

    # rolling correlation (last window)
    corr = log_ret.tail(vol_window).corr()

    # cumulative return current window
    cum_ret = (close.iloc[-1] / close.iloc[0] - 1) * 100

    # daily returns
    daily_ret = log_ret.tail(1).squeeze() * 100

    # spread proxy: (H-L)/mid in pips — requires intraday; here use daily range
    # We re-download daily OHLC for spread proxy
    return dict(
        log_ret=log_ret,
        ann_vol=ann_vol,
        corr=corr,
        cum_ret=cum_ret,
        daily_ret=daily_ret,
        close=close,
    )


@st.cache_data(ttl=300, show_spinner=False)
def fetch_ohlc(lookback_days: int) -> dict:
    end   = datetime.utcnow()
    start = end - timedelta(days=lookback_days + 5)
    raw   = yf.download(
        PAIR_TICKERS,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=True,
        progress=False,
    )
    out = {}
    for label, ticker in zip(SHORT_LABELS, PAIR_TICKERS):
        try:
            df = raw.xs(ticker, axis=1, level=1)[["Open","High","Low","Close"]].copy()
            df.dropna(inplace=True)
            out[label] = df.tail(lookback_days)
        except Exception:
            pass
    return out


def spread_proxy(ohlc: dict) -> pd.Series:
    """
    Daily range as pip-equivalent spread proxy:
    (High − Low) / pip_value  → average over last N sessions
    """
    spreads = {}
    for label, ticker in zip(SHORT_LABELS, PAIR_TICKERS):
        if label not in ohlc:
            continue
        df = ohlc[label]
        pv = pip_value(ticker)
        avg_spread = ((df["High"] - df["Low"]) / pv).mean()
        spreads[label] = round(avg_spread, 1)
    return pd.Series(spreads)

# ── chart builders ────────────────────────────────────────────────────────────

def fig_correlation(corr: pd.DataFrame) -> go.Figure:
    labels = SHORT_LABELS
    z      = corr.values
    text   = [[f"{v:.2f}" for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=labels,
        y=labels,
        text=text,
        texttemplate="%{text}",
        colorscale=[
            [0.0,  RED],
            [0.5,  BG],
            [1.0,  BLUE],
        ],
        zmin=-1, zmax=1,
        showscale=True,
        colorbar=dict(
            thickness=10,
            tickfont=dict(size=9, color=MUTED),
            outlinecolor=BORDER,
            outlinewidth=1,
        ),
        hovertemplate="<b>%{y} vs %{x}</b><br>Corr: %{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Rolling Correlation Matrix", font=dict(size=13, color=TEXT), x=0),
        height=440,
        margin=dict(l=12, r=12, t=40, b=12),
    )
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=10))
    return fig


def fig_volatility(ann_vol: pd.DataFrame, vol_window: int) -> go.Figure:
    fig = go.Figure()
    for label in SHORT_LABELS:
        if label not in ann_vol.columns:
            continue
        col   = PAIR_COLOURS.get(label, BLUE)
        series = ann_vol[label].dropna()
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            name=label,
            mode="lines",
            line=dict(color=col, width=1.6),
            hovertemplate=f"<b>{label}</b><br>Date: %{{x|%d %b %Y}}<br>Vol: %{{y:.2f}}%<extra></extra>",
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text=f"{vol_window}-Day Rolling Realised Volatility (Annualised %)",
            font=dict(size=13, color=TEXT), x=0,
        ),
        height=360,
        hovermode="x unified",
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], title="Vol %"),
    )
    return fig


def fig_spread_proxy(spreads: pd.Series) -> go.Figure:
    df  = spreads.sort_values(ascending=True).reset_index()
    df.columns = ["Pair", "Spread_pips"]
    cols = [PAIR_COLOURS.get(p, BLUE) for p in df["Pair"]]

    fig = go.Figure(go.Bar(
        x=df["Spread_pips"],
        y=df["Pair"],
        orientation="h",
        marker=dict(color=cols, opacity=0.85),
        text=[f"{v:.1f}" for v in df["Spread_pips"]],
        textposition="outside",
        textfont=dict(size=10, color=MUTED),
        hovertemplate="<b>%{y}</b><br>Avg Daily Range: %{x:.1f} pips<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Avg Daily Range (Pip Proxy)", font=dict(size=13, color=TEXT), x=0),
        height=360,
        xaxis=dict(**PLOTLY_LAYOUT["xaxis"], title="Pips"),
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], tickfont=dict(size=11, color=TEXT)),
    )
    return fig


def fig_ohlc_chart(df_ohlc: pd.DataFrame, pair_label: str,
                   bb_window: int = 20) -> go.Figure:
    close   = df_ohlc["Close"]
    ma      = close.rolling(bb_window).mean()
    std_    = close.rolling(bb_window).std()
    bb_up   = ma + 2 * std_
    bb_lo   = ma - 2 * std_

    col = PAIR_COLOURS.get(pair_label, BLUE)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.78, 0.22],
        vertical_spacing=0.03,
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df_ohlc.index,
        open=df_ohlc["Open"],
        high=df_ohlc["High"],
        low=df_ohlc["Low"],
        close=close,
        increasing_line_color=GREEN,
        decreasing_line_color=RED,
        increasing_fillcolor=GREEN,
        decreasing_fillcolor=RED,
        name="Price",
        showlegend=False,
    ), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df_ohlc.index, y=bb_up,
        mode="lines", line=dict(color=col, width=1, dash="dot"),
        name="BB Upper", opacity=0.6,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df_ohlc.index, y=bb_lo,
        mode="lines", line=dict(color=col, width=1, dash="dot"),
        fill="tonexty", fillcolor=f"rgba(88,166,255,0.06)",
        name="BB Lower", opacity=0.6,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df_ohlc.index, y=ma,
        mode="lines", line=dict(color=YELLOW, width=1.2),
        name=f"MA{bb_window}",
    ), row=1, col=1)

    # Daily return bars
    daily_r = close.pct_change() * 100
    bar_col  = [GREEN if v >= 0 else RED for v in daily_r]
    fig.add_trace(go.Bar(
        x=df_ohlc.index,
        y=daily_r,
        marker_color=bar_col,
        name="Daily Return %",
        showlegend=False,
    ), row=2, col=1)

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text=f"{pair_label.replace('=X','')} · Price & Bollinger Bands ({bb_window})",
            font=dict(size=13, color=TEXT), x=0,
        ),
        height=500,
        xaxis=dict(**PLOTLY_LAYOUT["xaxis"], rangeslider=dict(visible=False)),
        xaxis2=dict(gridcolor=BORDER, tickfont=dict(color=MUTED, size=10)),
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], title="Price"),
        yaxis2=dict(gridcolor=BORDER, tickfont=dict(color=MUTED, size=10), title="Ret %"),
        hovermode="x unified",
    )
    return fig


def fig_returns_dist(log_ret: pd.DataFrame, selected: list) -> go.Figure:
    fig = go.Figure()
    for label in selected:
        if label not in log_ret.columns:
            continue
        data = log_ret[label].dropna() * 100
        col  = PAIR_COLOURS.get(label, BLUE)
        fig.add_trace(go.Histogram(
            x=data,
            name=label,
            nbinsx=40,
            opacity=0.55,
            marker_color=col,
            hovertemplate=f"<b>{label}</b><br>Return: %{{x:.3f}}%<br>Count: %{{y}}<extra></extra>",
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Daily Log-Return Distribution", font=dict(size=13, color=TEXT), x=0),
        height=340,
        barmode="overlay",
        xaxis=dict(**PLOTLY_LAYOUT["xaxis"], title="Log Return (%)"),
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], title="Frequency"),
    )
    return fig


def fig_cumulative(close: pd.DataFrame, selected: list) -> go.Figure:
    fig = go.Figure()
    for label in selected:
        if label not in close.columns:
            continue
        norm = (close[label] / close[label].iloc[0] - 1) * 100
        col  = PAIR_COLOURS.get(label, BLUE)
        fig.add_trace(go.Scatter(
            x=norm.index,
            y=norm.values,
            name=label,
            mode="lines",
            line=dict(color=col, width=1.8),
            hovertemplate=f"<b>{label}</b><br>%{{x|%d %b %Y}}: %{{y:+.2f}}%<extra></extra>",
        ))
    fig.add_hline(y=0, line=dict(color=BORDER, width=1, dash="dash"))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Cumulative Performance (%)", font=dict(size=13, color=TEXT), x=0),
        height=320,
        hovermode="x unified",
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], title="Return (%)"),
    )
    return fig

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding: 16px 0 8px 0;">
          <div style="font-size:18px; font-weight:700; color:{TEXT};">⬡ FX Dashboard</div>
          <div style="font-size:11px; color:{MUTED}; margin-top:2px;">G10 · Real-Time Market Monitor</div>
        </div>
        <hr style="border-color:{BORDER}; margin: 8px 0 16px 0;">
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="section-label">Data Settings</div>', unsafe_allow_html=True)

    lookback = st.select_slider(
        "Lookback Period",
        options=[30, 60, 90, 180, 252],
        value=90,
        format_func=lambda x: {30:"1 Month", 60:"2 Months", 90:"3 Months",
                                180:"6 Months", 252:"1 Year"}[x],
    )

    vol_window = st.slider("Vol Window (days)", min_value=5, max_value=60, value=21, step=1)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">Chart Pair</div>', unsafe_allow_html=True)

    chart_pair_label = st.selectbox(
        "Select pair for OHLC",
        PAIR_LABELS,
        index=0,
        label_visibility="collapsed",
    )
    chart_pair_short  = chart_pair_label.replace("/", "")
    chart_pair_ticker = G10_PAIRS[chart_pair_label]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">Multi-Pair Overlay</div>', unsafe_allow_html=True)

    selected_pairs = st.multiselect(
        "Pairs for overlay charts",
        SHORT_LABELS,
        default=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⟳  Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="font-size:10px; color:{MUTED}; line-height:1.6;">
          Data via Yahoo Finance · 15-min delay<br>
          Refresh every 5 min automatically<br>
          <span style="color:{BORDER};">─────────────────</span><br>
          © {datetime.now().year} Ahmed Eladmi
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── main data fetch ───────────────────────────────────────────────────────────
with st.spinner(""):
    close   = fetch_fx(lookback)
    ohlc_d  = fetch_ohlc(lookback)
    metrics = compute_metrics(close, vol_window)
    spreads = spread_proxy(ohlc_d)

log_ret  = metrics["log_ret"]
ann_vol  = metrics["ann_vol"]
corr_mat = metrics["corr"]
daily_r  = metrics["daily_ret"]

# ── header ────────────────────────────────────────────────────────────────────
now_str = datetime.utcnow().strftime("%d %b %Y  %H:%M UTC")
st.markdown(
    f"""
    <div class="header-strip">
      <div>
        <div class="header-title">G10 FX Market Dashboard</div>
        <div class="header-sub"><span class="live-dot"></span>Last update: {now_str} · Data: Yahoo Finance (delayed)</div>
      </div>
      <div style="margin-left:auto; display:flex; gap:8px; align-items:center;">
        <span class="badge">G10 Pairs</span>
        <span class="badge">{lookback}d Lookback</span>
        <span class="badge">{vol_window}d Vol Window</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── live quote strip ──────────────────────────────────────────────────────────
st.markdown(f'<div class="section-label">Live Quotes</div>', unsafe_allow_html=True)

quote_cols = st.columns(len(SHORT_LABELS))
for i, (label, short) in enumerate(zip(PAIR_LABELS, SHORT_LABELS)):
    if short not in close.columns:
        continue
    price   = close[short].iloc[-1]
    prev    = close[short].iloc[-2]
    chg     = price - prev
    chg_pct = chg / prev * 100
    arrow   = "▲" if chg >= 0 else "▼"
    cls     = "pos" if chg >= 0 else "neg"

    # format price
    decimals = 3 if short in ("USDJPY","EURJPY","GBPJPY") else 5
    price_str = f"{price:.{decimals}f}"

    with quote_cols[i]:
        st.markdown(
            f"""
            <div class="quote-card">
              <div class="quote-pair">{label}</div>
              <div class="quote-price">{price_str}</div>
              <div class="quote-chg {cls}">{arrow} {chg_pct:+.3f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── summary metrics row ───────────────────────────────────────────────────────
st.markdown(f'<div class="section-label">Session Snapshot</div>', unsafe_allow_html=True)

best_pair  = metrics["cum_ret"].idxmax()
worst_pair = metrics["cum_ret"].idxmin()
best_val   = metrics["cum_ret"].max()
worst_val  = metrics["cum_ret"].min()

high_vol_pair = ann_vol.iloc[-1].idxmax()
high_vol_val  = ann_vol.iloc[-1].max()
low_vol_pair  = ann_vol.iloc[-1].idxmin()
low_vol_val   = ann_vol.iloc[-1].min()

# avg cross-correlation (excluding diagonal)
mask     = ~np.eye(corr_mat.shape[0], dtype=bool)
avg_corr = corr_mat.values[mask].mean()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(f"Best Performer ({lookback}d)",  f"{best_pair}",  f"{best_val:+.2f}%")
m2.metric(f"Worst Performer ({lookback}d)", f"{worst_pair}", f"{worst_val:+.2f}%")
m3.metric(f"Highest Vol",  f"{high_vol_pair}", f"{high_vol_val:.1f}% ann.")
m4.metric(f"Lowest Vol",   f"{low_vol_pair}",  f"{low_vol_val:.1f}% ann.")
m5.metric("Avg Cross-Corr", f"{avg_corr:.3f}", delta=None)

st.markdown("<br>", unsafe_allow_html=True)

# ── row 1: correlation | volatility ──────────────────────────────────────────
col_corr, col_vol = st.columns([1, 1.05])

with col_corr:
    st.markdown(f'<div class="section-label">Correlation</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_correlation(corr_mat), use_container_width=True, config={"displayModeBar": False})

with col_vol:
    st.markdown(f'<div class="section-label">Realised Volatility</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_volatility(ann_vol, vol_window), use_container_width=True, config={"displayModeBar": False})

# ── row 2: spread proxy | cumulative ─────────────────────────────────────────
col_sp, col_cum = st.columns([1, 1.05])

with col_sp:
    st.markdown(f'<div class="section-label">Daily Range Proxy (Pips)</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_spread_proxy(spreads), use_container_width=True, config={"displayModeBar": False})

with col_cum:
    st.markdown(f'<div class="section-label">Cumulative Returns</div>', unsafe_allow_html=True)
    eff_sel = selected_pairs if selected_pairs else SHORT_LABELS[:4]
    st.plotly_chart(fig_cumulative(close, eff_sel), use_container_width=True, config={"displayModeBar": False})

# ── row 3: OHLC chart full width ──────────────────────────────────────────────
st.markdown(f'<div class="section-label">Price Chart · {chart_pair_label}</div>', unsafe_allow_html=True)

if chart_pair_short in ohlc_d:
    st.plotly_chart(
        fig_ohlc_chart(ohlc_d[chart_pair_short], chart_pair_short),
        use_container_width=True,
        config={"displayModeBar": True, "displaylogo": False},
    )
else:
    st.info("OHLC data unavailable for this pair.")

# ── row 4: return distribution ────────────────────────────────────────────────
st.markdown(f'<div class="section-label">Return Distribution</div>', unsafe_allow_html=True)
eff_sel = selected_pairs if selected_pairs else SHORT_LABELS[:4]
st.plotly_chart(
    fig_returns_dist(log_ret, eff_sel),
    use_container_width=True,
    config={"displayModeBar": False},
)

# ── row 5: vol surface table ──────────────────────────────────────────────────
st.markdown(f'<div class="section-label">Volatility Regime Table</div>', unsafe_allow_html=True)

windows = [5, 10, 21, 42, 63]
tbl_rows = []
for label in SHORT_LABELS:
    if label not in log_ret.columns:
        continue
    row = {"Pair": label}
    for w in windows:
        vol_val = log_ret[label].tail(w).std() * np.sqrt(252) * 100
        row[f"{w}d Vol%"] = f"{vol_val:.2f}"
    # percentile rank of current 21d vol vs full history
    hist_vol = log_ret[label].rolling(21).std().dropna() * np.sqrt(252) * 100
    curr_vol = hist_vol.iloc[-1]
    rank     = (hist_vol < curr_vol).mean() * 100
    row["Vol Pctile"] = f"{rank:.0f}th"
    tbl_rows.append(row)

vol_df = pd.DataFrame(tbl_rows).set_index("Pair")

def colour_vol(val):
    try:
        v = float(val.replace("%",""))
        if v > 12:   return f"color: {RED}; font-weight:600"
        if v > 8:    return f"color: {ORANGE}"
        if v > 5:    return f"color: {YELLOW}"
        return f"color: {GREEN}"
    except Exception:
        return ""

def colour_pctile(val):
    try:
        v = float(val.replace("th","").replace("st","").replace("nd","").replace("rd",""))
        if v > 80:  return f"color: {RED}; font-weight:600"
        if v > 60:  return f"color: {ORANGE}"
        if v > 40:  return f"color: {YELLOW}"
        return f"color: {GREEN}"
    except Exception:
        return ""

styled = (
    vol_df.style
    .applymap(colour_vol, subset=[f"{w}d Vol%" for w in windows])
    .applymap(colour_pctile, subset=["Vol Pctile"])
    .set_table_styles([
        {"selector": "th",
         "props": [("background-color", SURFACE), ("color", MUTED),
                   ("font-size", "11px"), ("text-transform","uppercase"),
                   ("letter-spacing",".06em"), ("border-bottom", f"1px solid {BORDER}"),
                   ("padding","8px 12px")]},
        {"selector": "td",
         "props": [("background-color", BG), ("color", TEXT),
                   ("font-size","12px"), ("padding","7px 12px"),
                   ("border-bottom", f"1px solid {BORDER}"),
                   ("font-variant-numeric","tabular-nums")]},
        {"selector": "tr:hover td",
         "props": [("background-color", SURFACE)]},
    ])
    .set_properties(**{"text-align": "center"})
)

st.write(styled.to_html(), unsafe_allow_html=True)

# ── footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align:center; font-size:10px; color:{BORDER};
                padding: 16px 0; border-top: 1px solid {BORDER};">
      FX Market Dashboard · G10 · Ahmed Eladmi ·
      Data delayed 15 min via Yahoo Finance · Not financial advice
    </div>
    """,
    unsafe_allow_html=True,
)

# ── auto-refresh every 5 min ──────────────────────────────────────────────────
time.sleep(0)  # keeps the script alive for st.rerun scheduling
