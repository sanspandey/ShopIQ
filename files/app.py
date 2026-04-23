import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from data_processor import DataProcessor
from ai_analyzer import AIAnalyzer
from visualizer import Visualizer

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopIQ – AI Sales Analytics (Groq)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  h1, h2, h3, .big-title {
    font-family: 'Syne', sans-serif !important;
  }

  .stApp {
    background: #0a0d14;
    color: #e8e8f0;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0f1320 !important;
    border-right: 1px solid #1e2535;
  }

  [data-testid="stSidebar"] * {
    color: #c8cad8 !important;
  }

  /* Cards */
  .metric-card {
    background: linear-gradient(135deg, #141927 0%, #1a2035 100%);
    border: 1px solid #252d45;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
  }

  .metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: var(--accent);
    border-radius: 4px 0 0 4px;
  }

  .metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
  }

  .metric-label {
    font-size: 0.78rem;
    color: #6b7494;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 6px;
  }

  .metric-delta {
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 8px;
  }

  .delta-up   { color: #34d399; }
  .delta-down { color: #f87171; }
  .delta-flat { color: #94a3b8; }

  /* Section headers */
  .section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e8f0;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid #1e2535;
    padding-bottom: 12px;
    margin: 32px 0 20px;
  }

  /* AI insight box */
  .ai-insight {
    background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #3b82f6;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 12px 0;
    font-size: 0.95rem;
    line-height: 1.7;
    color: #cbd5e1;
  }

  .ai-insight .ai-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    color: #3b82f6;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
  }

  /* Alert box */
  .alert-box {
    background: linear-gradient(135deg, #1c1008 0%, #1a0f0a 100%);
    border: 1px solid #7c3016;
    border-left: 4px solid #f97316;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #fed7aa;
  }

  .good-box {
    background: linear-gradient(135deg, #071c13 0%, #071a14 100%);
    border: 1px solid #166534;
    border-left: 4px solid #22c55e;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #bbf7d0;
  }

  /* Upload area */
  .upload-hero {
    text-align: center;
    padding: 60px 20px;
    background: linear-gradient(135deg, #0f1320 0%, #141927 100%);
    border: 2px dashed #252d45;
    border-radius: 24px;
    margin: 40px 0;
  }

  .upload-hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 12px;
  }

  .upload-hero p {
    color: #6b7494;
    font-size: 1.05rem;
    max-width: 480px;
    margin: 0 auto 32px;
    line-height: 1.7;
  }

  /* Plotly chart background */
  .js-plotly-plot .plotly .main-svg {
    border-radius: 12px;
  }

  /* Forecast badge */
  .forecast-badge {
    display: inline-block;
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.3);
    color: #a78bfa;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 20px;
    margin-bottom: 16px;
  }

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"] {
    background: #0f1320;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
  }

  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6b7494;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .stTabs [aria-selected="true"] {
    background: #1e2535 !important;
    color: #e8e8f0 !important;
  }

  .stFileUploader {
    background: #0f1320 !important;
    border-radius: 12px !important;
  }

  /* Hide Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "processed" not in st.session_state:
    st.session_state.processed = None
if "ai_results" not in st.session_state:
    st.session_state.ai_results = None


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 8px 0 24px'>
      <div style='font-family: Syne, sans-serif; font-size: 1.5rem; font-weight: 800;
                  background: linear-gradient(135deg, #60a5fa, #a78bfa);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  background-clip: text;'>
        📊 ShopIQ
      </div>
      <div style='font-size: 0.72rem; color: #6b7494; letter-spacing: 2px;
                  text-transform: uppercase; margin-top: 2px;'>
        AI Sales Analytics
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Upload Your Sales File**")
    uploaded_file = st.file_uploader(
        "Excel or CSV file",
        type=["xlsx", "xls", "csv"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.success(f"✓ {uploaded_file.name}")

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.8rem; color: #4a5070; line-height: 1.6;'>
      <b style='color: #6b7494'>Supported formats</b><br>
      • Excel (.xlsx, .xls)<br>
      • CSV (.csv)<br><br>
      <b style='color: #6b7494'>Auto-detected columns</b><br>
      • Dates, Revenue, Quantity<br>
      • Products, Categories<br>
      • Any named columns
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    forecast_periods = st.slider("Forecast months ahead", 1, 6, 3)
    show_raw = st.checkbox("Show cleaned data table", False)


# ─── Main Content ─────────────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("""
    <div class='upload-hero'>
      <h1>Turn Your Sales Data<br>Into Clear Insights</h1>
      <p>Upload any Excel or CSV file with your sales records.
         ShopIQ will automatically clean, analyse, and explain
         your business performance in plain English.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class='metric-card' style='--accent:#60a5fa'>
          <div style='font-size:1.8rem;margin-bottom:8px'>🧹</div>
          <div style='font-family:Syne,sans-serif;font-weight:700;color:#e8e8f0;font-size:1rem'>
            Auto Data Cleaning
          </div>
          <div style='color:#6b7494;font-size:0.85rem;margin-top:6px;line-height:1.5'>
            Handles missing values, wrong formats, and duplicate rows automatically.
          </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='metric-card' style='--accent:#a78bfa'>
          <div style='font-size:1.8rem;margin-bottom:8px'>🤖</div>
          <div style='font-family:Syne,sans-serif;font-weight:700;color:#e8e8f0;font-size:1rem'>
            AI-Powered Insights
          </div>
          <div style='color:#6b7494;font-size:0.85rem;margin-top:6px;line-height:1.5'>
            Plain-language summaries, trend alerts, and revenue forecasts.
          </div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='metric-card' style='--accent:#34d399'>
          <div style='font-size:1.8rem;margin-bottom:8px'>📈</div>
          <div style='font-family:Syne,sans-serif;font-weight:700;color:#e8e8f0;font-size:1rem'>
            Smart Dashboards
          </div>
          <div style='color:#6b7494;font-size:0.85rem;margin-top:6px;line-height:1.5'>
            Interactive charts for trends, products, and performance gaps.
          </div>
        </div>""", unsafe_allow_html=True)

    st.stop()


# ─── Load & Process ──────────────────────────────────────────────────────────
processor = DataProcessor()
visualizer = Visualizer()

with st.spinner("Reading and cleaning your data…"):
    try:
        df_raw = processor.load_file(uploaded_file)
        df, meta = processor.auto_detect_and_clean(df_raw)
        st.session_state.df = df
        st.session_state.meta = meta
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

df   = st.session_state.df
meta = st.session_state.meta


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:space-between;
            border-bottom: 1px solid #1e2535; padding-bottom: 20px; margin-bottom: 8px'>
  <div>
    <div style='font-family:Syne,sans-serif; font-size:1.8rem; font-weight:800; color:#e8e8f0'>
      Sales Dashboard
    </div>
    <div style='color:#6b7494; font-size:0.85rem; margin-top:4px'>
      {uploaded_file.name} &nbsp;·&nbsp; {len(df):,} records &nbsp;·&nbsp;
      {meta.get("date_range","—")}
    </div>
  </div>
  <div style='font-size:0.72rem; color:#4a5070; text-align:right; line-height:1.8'>
    Columns detected<br>
    <span style='color:#6b7494'>{" · ".join(meta.get("detected_cols",{}).values())}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── KPI Cards ───────────────────────────────────────────────────────────────
stats = processor.compute_kpis(df, meta)

c1, c2, c3, c4 = st.columns(4)
def kpi_card(col, accent, icon, value, label, delta=None, delta_dir="flat"):
    dir_cls = {"up":"delta-up","down":"delta-down","flat":"delta-flat"}[delta_dir]
    delta_html = f"<div class='metric-delta {dir_cls}'>{delta}</div>" if delta else ""
    col.markdown(f"""
    <div class='metric-card' style='--accent:{accent}'>
      <div style='font-size:1.4rem;margin-bottom:6px'>{icon}</div>
      <div class='metric-value'>{value}</div>
      <div class='metric-label'>{label}</div>
      {delta_html}
    </div>""", unsafe_allow_html=True)

kpi_card(c1,"#60a5fa","💰", stats["total_revenue"], "Total Revenue",
         stats.get("revenue_delta"), stats.get("revenue_dir","flat"))
kpi_card(c2,"#34d399","📦", stats["total_orders"],  "Total Orders",
         stats.get("orders_delta"), stats.get("orders_dir","flat"))
kpi_card(c3,"#a78bfa","🛍️", stats["avg_order"],     "Avg Order Value",
         stats.get("avg_delta"), stats.get("avg_dir","flat"))
kpi_card(c4,"#f59e0b","⭐", stats["top_product"],   "Best-Selling Product")


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🛍️ Products", "🔮 Forecast", "🤖 AI Insights"])


# ══ TAB 1: Trends ══
with tab1:
    st.markdown("<div class='section-header'>Revenue Over Time</div>", unsafe_allow_html=True)
    fig_trend = visualizer.revenue_trend(df, meta)
    st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Monthly Comparison</div>", unsafe_allow_html=True)
        fig_bar = visualizer.monthly_bar(df, meta)
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.markdown("<div class='section-header'>Sales by Day of Week</div>", unsafe_allow_html=True)
        fig_dow = visualizer.day_of_week(df, meta)
        st.plotly_chart(fig_dow, use_container_width=True)


# ══ TAB 2: Products ══
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Top Products by Revenue</div>", unsafe_allow_html=True)
        fig_prod = visualizer.top_products(df, meta)
        if fig_prod:
            st.plotly_chart(fig_prod, use_container_width=True)
        else:
            st.info("No product column detected in your data.")
    with col2:
        st.markdown("<div class='section-header'>Revenue Share</div>", unsafe_allow_html=True)
        fig_pie = visualizer.product_pie(df, meta)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True)

    if meta.get("category_col"):
        st.markdown("<div class='section-header'>Category Performance</div>", unsafe_allow_html=True)
        fig_cat = visualizer.category_heatmap(df, meta)
        if fig_cat:
            st.plotly_chart(fig_cat, use_container_width=True)


# ══ TAB 3: Forecast ══
with tab3:
    st.markdown(f"<div class='forecast-badge'>🔮 AI Forecast — {forecast_periods} months ahead</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Revenue Forecast</div>", unsafe_allow_html=True)

    fig_fc, forecast_df = visualizer.revenue_forecast(df, meta, periods=forecast_periods)
    st.plotly_chart(fig_fc, use_container_width=True)

    if forecast_df is not None and not forecast_df.empty:
        st.markdown("<div class='section-header'>Forecast Table</div>", unsafe_allow_html=True)
        fc_display = forecast_df.copy()
        fc_display.columns = ["Month", "Forecasted Revenue", "Lower Bound", "Upper Bound"]
        st.dataframe(
            fc_display.style.format({
                "Forecasted Revenue": "₹{:,.0f}",
                "Lower Bound":       "₹{:,.0f}",
                "Upper Bound":       "₹{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True
        )


# ══ TAB 4: AI Insights ══
with tab4:
    analyzer = AIAnalyzer()

    with st.spinner("Asking Groq AI for insights…"):
        if st.session_state.ai_results is None:
            ai_out = analyzer.generate_insights(df, meta, stats, forecast_df if 'forecast_df' in dir() else None)
            st.session_state.ai_results = ai_out
        ai = st.session_state.ai_results

    # Summary
    st.markdown("<div class='section-header'>Business Summary</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='ai-insight'>
      <div class='ai-label'>🤖 AI Analysis</div>
      {ai.get("summary","No summary available.")}
    </div>""", unsafe_allow_html=True)

    # Alerts
    alerts = ai.get("alerts", [])
    if alerts:
        st.markdown("<div class='section-header'>⚠️ Trend Alerts</div>", unsafe_allow_html=True)
        for a in alerts:
            st.markdown(f"<div class='alert-box'>⚠️ {a}</div>", unsafe_allow_html=True)

    # Positives
    positives = ai.get("positives", [])
    if positives:
        st.markdown("<div class='section-header'>✅ What's Working</div>", unsafe_allow_html=True)
        for p in positives:
            st.markdown(f"<div class='good-box'>✅ {p}</div>", unsafe_allow_html=True)

    # Recommendations
    recs = ai.get("recommendations", [])
    if recs:
        st.markdown("<div class='section-header'>💡 Recommendations</div>", unsafe_allow_html=True)
        for i, r in enumerate(recs, 1):
            st.markdown(f"""
            <div class='ai-insight' style='border-left-color:#a78bfa'>
              <div class='ai-label'>Suggestion {i}</div>
              {r}
            </div>""", unsafe_allow_html=True)

    # Forecast note
    fc_note = ai.get("forecast_note")
    if fc_note:
        st.markdown("<div class='section-header'>🔮 Forecast Interpretation</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='ai-insight' style='border-left-color:#34d399'>
          <div class='ai-label'>Forecast Analysis</div>
          {fc_note}
        </div>""", unsafe_allow_html=True)


# ─── Raw Data ─────────────────────────────────────────────────────────────────
if show_raw:
    st.markdown("<div class='section-header'>Cleaned Data Preview</div>", unsafe_allow_html=True)
    st.dataframe(df.head(200), use_container_width=True)
