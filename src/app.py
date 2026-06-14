import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from predict import ChurnPredictor
from retention import retention_strategy
from report import generate_pdf

st.set_page_config(
    page_title="NEXUS · Retention Intelligence",
    layout="wide",
    page_icon="⬡",
    initial_sidebar_state="collapsed",
)

@st.cache_resource
def load_predictor():
    return ChurnPredictor()

predictor = load_predictor()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=JetBrains+Mono:wght@300;400;500;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');

:root {
  --black:      #060608;
  --g950:       #0c0c0f;
  --g900:       #111115;
  --g850:       #16161b;
  --g800:       #1c1c22;
  --g700:       #26262e;
  --g600:       #32323c;
  --g500:       #4a4a58;
  --g400:       #6b6b7e;
  --g300:       #9898aa;
  --g100:       #e8e8f0;
  --red:        #dc2626;
  --red-dark:   #7f1d1d;
  --red-lite:   #f87171;
  --red-glow:   rgba(220,38,38,0.16);
  --red-glow2:  rgba(220,38,38,0.06);
  --amber:      #d97706;
  --amber-dim:  rgba(217,119,6,0.12);
  --green:      #059669;
  --green-dim:  rgba(5,150,105,0.12);
  --text:       #c8c8d8;
  --text-hi:    #f0f0f8;
  --text-dim:   #4a4a58;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
  background-color: var(--black) !important;
  color: var(--text) !important;
  font-family: 'Manrope', sans-serif !important;
  -webkit-font-smoothing: antialiased;
}

/* Ambient red glow at top */
.stApp::after {
  content: '';
  position: fixed; top: -180px; left: 50%; transform: translateX(-50%);
  width: 900px; height: 360px;
  background: radial-gradient(ellipse, rgba(220,38,38,0.055) 0%, transparent 70%);
  pointer-events: none; z-index: 0;
}

.block-container {
  position: relative; z-index: 1;
  padding: 0 2.6rem 6rem 2.6rem !important;
  max-width: 1460px !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--g950); }
::-webkit-scrollbar-thumb { background: var(--g700); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--red); }

@keyframes fadeUp {
  from { opacity:0; transform:translateY(20px); }
  to   { opacity:1; transform:translateY(0);    }
}
@keyframes fadeIn {
  from { opacity:0; }
  to   { opacity:1; }
}
@keyframes scaleX-in {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}
@keyframes pulse-dot {
  0%,100% { box-shadow: 0 0 0 0 var(--red-glow); }
  50%      { box-shadow: 0 0 0 7px transparent;   }
}
@keyframes float {
  0%,100% { transform:translateY(0);  }
  50%      { transform:translateY(-5px); }
}
@keyframes scan {
  from { top:-60px; }
  to   { top:120%;  }
}
@keyframes countUp {
  from { opacity:0; transform:translateY(8px); }
  to   { opacity:1; transform:translateY(0);   }
}
@keyframes barGrow {
  from { width:0; }
  to   { width:100%; }
}
@keyframes shimmer {
  0%   { background-position:-500px 0; }
  100% { background-position: 500px 0; }
}

/* Staggered entrance */
.block-container>div:nth-child(1)  { animation:fadeUp .30s ease .00s both; }
.block-container>div:nth-child(2)  { animation:fadeUp .30s ease .04s both; }
.block-container>div:nth-child(3)  { animation:fadeUp .30s ease .08s both; }
.block-container>div:nth-child(4)  { animation:fadeUp .30s ease .12s both; }
.block-container>div:nth-child(5)  { animation:fadeUp .30s ease .16s both; }
.block-container>div:nth-child(6)  { animation:fadeUp .30s ease .20s both; }
.block-container>div:nth-child(7)  { animation:fadeUp .30s ease .24s both; }
.block-container>div:nth-child(8)  { animation:fadeUp .30s ease .28s both; }
.block-container>div:nth-child(n+9){ animation:fadeUp .30s ease .32s both; }

h1,h2,h3 {
  font-family:'Bebas Neue',sans-serif !important;
  letter-spacing:3px !important;
  color:var(--text-hi) !important;
  font-weight:400 !important;
  margin:0 !important;
}
h1 { font-size:3rem   !important; line-height:1  !important; }
h2 { font-size:1.55rem !important; }
h3 { font-size:1.1rem  !important; }
p  { color:var(--text); line-height:1.7; }

/* ══ Buttons ════════════════════════════════════════════════════════════════ */
.stButton>button {
  background:var(--g900) !important;
  border:1px solid var(--g700) !important;
  color:var(--g300) !important;
  border-radius:5px !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.64rem !important;
  letter-spacing:2.5px !important;
  text-transform:uppercase !important;
  padding:10px 20px !important;
  width:100% !important;
  transition:all .22s cubic-bezier(.4,0,.2,1) !important;
  position:relative !important; overflow:hidden !important;
}
.stButton>button::before {
  content:'';
  position:absolute; left:0; top:0;
  width:3px; height:100%; background:var(--red);
  transform:scaleY(0); transform-origin:bottom;
  transition:transform .22s ease;
}
.stButton>button:hover::before { transform:scaleY(1); }
.stButton>button:hover {
  border-color:var(--red) !important;
  color:var(--text-hi) !important;
  background:var(--g850) !important;
  box-shadow:0 0 0 1px var(--red-glow),inset 0 0 18px var(--red-glow2) !important;
  transform:translateY(-1px) !important;
}
.stButton>button:active { transform:translateY(0) !important; }

/* Download button */
[data-testid="stDownloadButton"]>button {
  border-color:var(--red) !important; color:var(--red-lite) !important;
  background:var(--g900) !important;
}
[data-testid="stDownloadButton"]>button:hover {
  background:var(--red-glow2) !important;
  box-shadow:0 0 18px var(--red-glow) !important;
  color:var(--red-lite) !important;
}

/* ══ Metrics ════════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
  background:var(--g900) !important; border:1px solid var(--g700) !important;
  border-radius:8px !important; padding:22px 24px !important;
  position:relative !important; overflow:hidden !important;
  transition:border-color .2s,box-shadow .2s !important;
  animation:countUp .45s ease both !important;
}
[data-testid="stMetric"]::after {
  content:''; position:absolute; bottom:0; left:0; right:0; height:1px;
  background:linear-gradient(to right,transparent,var(--red),transparent);
}
[data-testid="stMetric"]:hover {
  border-color:var(--g600) !important;
  box-shadow:0 6px 28px rgba(0,0,0,.5) !important;
}
[data-testid="stMetricLabel"] {
  color:var(--g400) !important; font-family:'JetBrains Mono',monospace !important;
  font-size:0.57rem !important; letter-spacing:2.5px !important; text-transform:uppercase !important;
}
[data-testid="stMetricValue"] {
  font-family:'Bebas Neue',sans-serif !important; font-size:2.1rem !important;
  color:var(--text-hi) !important; letter-spacing:2px !important;
}

/* ══ Inputs ═════════════════════════════════════════════════════════════════ */
input,.stTextInput input,.stNumberInput input {
  background:var(--g900) !important; border:1px solid var(--g700) !important;
  color:var(--text-hi) !important; border-radius:5px !important;
  font-family:'JetBrains Mono',monospace !important; font-size:0.8rem !important;
  transition:border-color .2s,box-shadow .2s !important;
}
input:focus,.stTextInput input:focus,.stNumberInput input:focus {
  border-color:var(--red) !important;
  box-shadow:0 0 0 3px var(--red-glow) !important; outline:none !important;
}
label,.stTextInput label,.stNumberInput label {
  color:var(--g400) !important; font-family:'JetBrains Mono',monospace !important;
  font-size:0.59rem !important; letter-spacing:2px !important; text-transform:uppercase !important;
}
/* Selectbox */
[data-testid="stSelectbox"] > div > div {
  background:var(--g900) !important; border:1px solid var(--g700) !important;
  border-radius:5px !important; color:var(--text) !important;
}

/* ══ File uploader ══════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
  background:var(--g900) !important; border:1.5px dashed var(--g600) !important;
  border-radius:8px !important; padding:10px !important;
  transition:border-color .2s,background .2s !important;
}
[data-testid="stFileUploader"]:hover {
  border-color:var(--red) !important; background:var(--red-glow2) !important;
}

/* ══ Dataframe ══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
  border:1px solid var(--g700) !important; border-radius:8px !important;
  overflow:hidden !important; animation:fadeIn .4s ease both !important;
}

/* ══ Alerts ═════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] { border-radius:7px !important; }

/* ══ Custom components ══════════════════════════════════════════════════════ */

/* Header */
.nx-header {
  display:flex; align-items:center; gap:18px;
  padding:30px 0 22px; border-bottom:1px solid var(--g800);
  margin-bottom:34px; animation:fadeIn .5s ease both;
}
.nx-hex {
  position:relative; width:48px; height:48px; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  animation:float 4s ease-in-out infinite;
}
.nx-hex:hover { animation:none; transform:rotate(30deg); transition:transform .4s ease; }
.nx-hex-text {
  position:relative; z-index:1;
  font-family:'Bebas Neue',sans-serif; font-size:16px; color:var(--text-hi); letter-spacing:1px;
}
.nx-wordmark { display:flex; flex-direction:column; gap:3px; }
.nx-title {
  font-family:'Bebas Neue',sans-serif; font-size:1.45rem;
  letter-spacing:5px; text-transform:uppercase; color:var(--text-hi); margin:0; line-height:1;
}
.nx-sub {
  font-family:'JetBrains Mono',monospace; font-size:0.57rem;
  letter-spacing:3px; text-transform:uppercase; color:var(--g500); margin:0;
}
.nx-status {
  margin-left:auto; display:flex; align-items:center; gap:8px;
  padding:6px 14px; border:1px solid var(--g700);
  border-radius:4px; background:var(--g900);
}
.nx-dot {
  width:6px; height:6px; border-radius:50%; background:var(--red);
  animation:pulse-dot 2.2s ease-in-out infinite;
}
.nx-status-text {
  font-family:'JetBrains Mono',monospace; font-size:0.57rem;
  letter-spacing:2px; text-transform:uppercase; color:var(--g400);
}

/* Section label */
.nx-section {
  display:flex; align-items:center; gap:12px; margin:30px 0 14px;
}
.nx-sec-line {
  width:22px; height:1px; background:var(--red);
  transform-origin:left; animation:scaleX-in .4s ease both;
}
.nx-sec-label {
  font-family:'JetBrains Mono',monospace; font-size:0.59rem;
  letter-spacing:3.5px; text-transform:uppercase; color:var(--g500); margin:0;
}
.nx-sec-end { flex:1; height:1px; background:var(--g800); }

/* Divider */
.nx-div {
  position:relative; height:1px; background:var(--g800); margin:28px 0;
}
.nx-div::before {
  content:''; position:absolute; left:50%; top:0; transform:translateX(-50%);
  width:100px; height:1px; background:linear-gradient(to right,transparent,var(--red),transparent);
}
.nx-div::after {
  content:''; position:absolute; left:50%; top:50%;
  transform:translate(-50%,-50%); width:5px; height:5px;
  border-radius:50%; background:var(--red); box-shadow:0 0 8px var(--red);
}

/* Stat card */
.nx-card {
  background:var(--g900); border:1px solid var(--g700); border-radius:8px;
  padding:26px 26px 22px; position:relative; overflow:hidden;
  transition:border-color .22s,box-shadow .22s,transform .22s;
  animation:fadeUp .4s ease both;
}
.nx-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(to right,var(--red),transparent);
  transform-origin:left; animation:scaleX-in .5s ease both;
}
.nx-card::after {
  content:''; position:absolute; left:0; right:0; height:50px;
  background:linear-gradient(to bottom,transparent,rgba(220,38,38,.025),transparent);
  animation:scan 5s linear infinite; pointer-events:none;
}
.nx-card:hover {
  border-color:var(--g600);
  box-shadow:0 8px 36px rgba(0,0,0,.55),0 0 0 1px var(--g700);
  transform:translateY(-3px);
}
.nx-card-tag {
  font-family:'JetBrains Mono',monospace; font-size:0.57rem;
  letter-spacing:3px; text-transform:uppercase; color:var(--g500); margin:0 0 10px;
}
.nx-card-val {
  font-family:'Bebas Neue',sans-serif; font-size:2.5rem;
  letter-spacing:2px; color:var(--text-hi); margin:0; line-height:1;
  animation:countUp .5s ease both;
}
.nx-badge {
  display:inline-flex; align-items:center; gap:5px;
  margin-top:10px; padding:3px 10px; border-radius:3px;
  font-family:'JetBrains Mono',monospace; font-size:0.54rem; letter-spacing:1.5px; text-transform:uppercase;
}
.badge-red   { background:var(--red-glow);  color:var(--red-lite); border:1px solid rgba(220,38,38,.2); }
.badge-green { background:var(--green-dim); color:#34d399;         border:1px solid rgba(5,150,105,.2); }
.badge-amber { background:var(--amber-dim); color:#fbbf24;         border:1px solid rgba(217,119,6,.2); }

/* Retention card */
.ret-card {
  background:var(--g900); border:1px solid var(--g700); border-left:2px solid var(--red);
  border-radius:6px; padding:13px 17px; margin-bottom:9px;
  font-size:0.875rem; line-height:1.7; color:var(--text);
  transition:border-left-color .2s,background .2s,transform .2s;
  animation:fadeUp .35s ease both;
}
.ret-card:hover {
  background:var(--g850); border-left-color:var(--red-lite); transform:translateX(4px);
}

/* Customer block */
.cust-block {
  background:var(--g900); border:1px solid var(--g700); border-radius:8px;
  padding:16px 20px 12px; margin-bottom:7px;
  transition:border-color .2s; animation:fadeUp .35s ease both;
}
.cust-block:hover { border-color:var(--g600); }
.cust-hdr { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.cust-num {
  font-family:'JetBrains Mono',monospace; font-size:0.58rem;
  letter-spacing:2px; text-transform:uppercase; color:var(--g500);
}
.cust-sep { flex:1; height:1px; background:var(--g800); }
.cust-prob {
  font-family:'Bebas Neue',sans-serif; font-size:1rem; letter-spacing:2px; color:var(--red-lite);
}
.prog-track { background:var(--g800); border-radius:2px; height:3px; overflow:hidden; }
.prog-fill {
  height:100%; border-radius:2px; background:var(--red);
  transform-origin:left; animation:scaleX-in .7s cubic-bezier(.4,0,.2,1) both;
}

/* Risk display (manual page) */
.nx-risk-block {
  background:var(--g900); border:1px solid var(--g700); border-radius:8px;
  padding:26px 28px; position:relative; overflow:hidden; animation:fadeUp .4s ease both;
}
.nx-risk-block::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:var(--red); animation:scaleX-in .5s ease both; transform-origin:left;
}
.nx-risk-tag {
  font-family:'JetBrains Mono',monospace; font-size:0.57rem;
  letter-spacing:2.5px; text-transform:uppercase; color:var(--g500); margin:0 0 7px;
}
.nx-risk-val {
  font-family:'Bebas Neue',sans-serif; font-size:2.8rem;
  letter-spacing:2px; margin:0; line-height:1; animation:countUp .5s ease both;
}
.risk-high   { color:var(--red-lite); text-shadow:0 0 24px var(--red-glow); }
.risk-medium { color:#fbbf24;         text-shadow:0 0 24px var(--amber-dim); }
.risk-low    { color:#34d399;         text-shadow:0 0 24px var(--green-dim); }

/* Loader */
.nx-loader {
  font-family:'JetBrains Mono',monospace; font-size:0.8rem;
  letter-spacing:3px; color:var(--red); text-transform:uppercase;
  animation:pulse-dot 1.2s ease-in-out infinite;
}

/* Empty state */
.nx-empty {
  text-align:center; padding:60px 28px;
  border:1.5px dashed var(--g700); border-radius:8px; animation:fadeIn .5s ease both;
}
.nx-empty-icon { font-size:2.6rem; margin-bottom:14px; opacity:.28; }
.nx-empty-title {
  font-family:'Bebas Neue',sans-serif; font-size:1.35rem; letter-spacing:3px;
  color:var(--g500); margin:0 0 8px;
}
.nx-empty-sub {
  font-family:'JetBrains Mono',monospace; font-size:0.62rem; letter-spacing:1.5px;
  line-height:1.8; color:var(--g600); max-width:340px; margin:0 auto;
}

/* AI Verdict */
.nx-verdict {
  padding:16px 20px; border-radius:7px; margin:10px 0;
  display:flex; align-items:center; gap:12px;
  font-family:'JetBrains Mono',monospace; font-size:0.72rem; letter-spacing:2px; text-transform:uppercase;
  animation:fadeIn .4s ease both;
}
.verdict-ok   { background:rgba(5,150,105,.1); border:1px solid rgba(5,150,105,.25); color:#34d399; }
.verdict-warn { background:var(--red-glow);    border:1px solid rgba(220,38,38,.25);  color:var(--red-lite); }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "df_result"  not in st.session_state: st.session_state.df_result  = None
if "page"       not in st.session_state: st.session_state.page       = "dashboard"

# ── Helpers ───────────────────────────────────────────────────────────────────
def churn_risk(prob):
    if prob < 0.3:   return "Low Risk"
    elif prob < 0.6: return "Medium Risk"
    else:            return "High Risk"

def risk_css(level):
    return {"High Risk":"risk-high","Medium Risk":"risk-medium","Low Risk":"risk-low"}.get(level,"")

def risk_color(level):
    return {"High Risk":"#f87171","Medium Risk":"#fbbf24","Low Risk":"#34d399"}.get(level,"#9898aa")

def safe_prepare(df):
    df = df.copy()
    for col in df.columns:
        if "id" in col.lower():
            df = df.drop(columns=[col])
    try:
        df_model = predictor.prepare_features(df)
    except Exception:
        df_model = df.reindex(columns=predictor.features, fill_value=0)
    return df, df_model

# Plotly dark template
def plotly_dark():
    return dict(
        plot_bgcolor  = "rgba(0,0,0,0)",
        paper_bgcolor = "rgba(0,0,0,0)",
        font_color    = "#9898aa",
        font_family   = "JetBrains Mono",
        margin        = dict(l=16, r=16, t=46, b=16),
        xaxis=dict(
            gridcolor="#1c1c22", linecolor="#1c1c22", zerolinecolor="#1c1c22",
            tickfont=dict(size=10, family="JetBrains Mono"),
        ),
        yaxis=dict(
            gridcolor="#1c1c22", linecolor="#1c1c22", zerolinecolor="#1c1c22",
            tickfont=dict(size=10, family="JetBrains Mono"),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", bordercolor="#26262e", borderwidth=1,
            font=dict(family="JetBrains Mono", size=10),
        ),
        hoverlabel=dict(
            bgcolor="#16161b", bordercolor="#32323c",
            font_family="JetBrains Mono", font_size=11,
        ),
    )

# UI helpers
def section(label):
    st.markdown(f"""
<div class="nx-section">
  <div class="nx-sec-line"></div>
  <p class="nx-sec-label">{label}</p>
  <div class="nx-sec-end"></div>
</div>""", unsafe_allow_html=True)

def divider():
    st.markdown('<div class="nx-div"></div>', unsafe_allow_html=True)

def ret_card(text):
    st.markdown(f'<div class="ret-card">{text}</div>', unsafe_allow_html=True)

def empty_state(icon, title, sub):
    st.markdown(f"""
<div class="nx-empty">
  <div class="nx-empty-icon">{icon}</div>
  <p class="nx-empty-title">{title}</p>
  <p class="nx-empty-sub">{sub}</p>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="nx-header">
  <div class="nx-hex">
    <svg width="48" height="48" viewBox="0 0 48 48" style="position:absolute">
      <polygon points="24,2 44,13 44,35 24,46 4,35 4,13"
               fill="none" stroke="#dc2626" stroke-width="1.5" opacity=".9"/>
      <polygon points="24,9 38,17 38,31 24,39 10,31 10,17"
               fill="none" stroke="#dc2626" stroke-width=".5" opacity=".3"/>
    </svg>
    <span class="nx-hex-text">NX</span>
  </div>
  <div class="nx-wordmark">
    <p class="nx-title">NEXUS</p>
    <p class="nx-sub">Retention Intelligence Platform · v2.0</p>
  </div>
  <div class="nx-status">
    <div class="nx-dot"></div>
    <span class="nx-status-text">System Active</span>
  </div>
</div>""", unsafe_allow_html=True)

# ── Nav ───────────────────────────────────────────────────────────────────────
n1, n2, n3, _ = st.columns([1, 1, 1, 7])
with n1:
    if st.button("⬡  Dashboard"): st.session_state.page = "dashboard"
with n2:
    if st.button("⬡  Batch"):     st.session_state.page = "batch"
with n3:
    if st.button("⬡  Manual"):    st.session_state.page = "manual"

divider()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":

    st.markdown("""
<div style="margin-bottom:38px;animation:fadeUp .4s ease both">
  <h1 style="font-size:2.8rem;letter-spacing:4px">AI CUSTOMER<br>RETENTION INTELLIGENCE</h1>
  <p style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;letter-spacing:3px;
            color:#4a4a58;text-transform:uppercase;margin-top:14px">
    Precision &nbsp;·&nbsp; Strength &nbsp;·&nbsp; Reliability
  </p>
</div>""", unsafe_allow_html=True)

    section("What This System Does")
    st.markdown("""
<div class="nx-card" style="margin-bottom:20px">
  <p style="color:#9898aa;font-size:0.9rem;line-height:1.8;margin:0">
    NEXUS is an AI-powered churn prediction and customer retention platform. Upload any customer
    CSV to score your entire cohort, identify at-risk accounts, and receive personalised retention
    strategies — all backed by a trained Random Forest model and explainable AI insights.
  </p>
</div>""", unsafe_allow_html=True)

    divider()
    section("System Status")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
<div class="nx-card">
  <p class="nx-card-tag">Model</p>
  <p class="nx-card-val">Random Forest</p>
  <span class="nx-badge badge-green">● Operational</span>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
<div class="nx-card">
  <p class="nx-card-tag">Pipeline</p>
  <p class="nx-card-val">Active</p>
  <span class="nx-badge badge-red">● Live</span>
</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
<div class="nx-card">
  <p class="nx-card-tag">Features Loaded</p>
  <p class="nx-card-val">{len(predictor.features)}</p>
  <span class="nx-badge badge-amber">● Configured</span>
</div>""", unsafe_allow_html=True)

    divider()
    section("Platform Guide")
    g1, g2, g3 = st.columns(3)
    for col, num, title, desc in [
        (g1, "01", "Dashboard",       "System health, model status, and platform overview."),
        (g2, "02", "Batch Prediction","Upload a customer CSV to score the entire cohort. Get risk levels, feature importance, retention strategies, and a downloadable PDF report."),
        (g3, "03", "Manual Entry",    "Enter a single customer record for instant churn probability, gauge visualisation, and personalised retention actions."),
    ]:
        col.markdown(f"""
<div class="nx-card" style="padding:22px 22px">
  <p style="font-family:'Bebas Neue',sans-serif;font-size:1.9rem;
            letter-spacing:2px;color:#26262e;margin:0 0 10px;line-height:1">{num}</p>
  <p class="nx-card-tag" style="margin-bottom:8px">{title}</p>
  <p style="font-size:0.83rem;color:#6b6b7e;line-height:1.7;margin:0">{desc}</p>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BATCH
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "batch":

    st.markdown("<h2 style='margin-bottom:26px'>Batch Prediction</h2>", unsafe_allow_html=True)

    section("Upload Dataset")
    uploaded_file = st.file_uploader("Drop CSV here", type=["csv"], label_visibility="collapsed")

    if not uploaded_file:
        st.markdown("<br>", unsafe_allow_html=True)
        empty_state("⬡", "No File Loaded",
                    "Upload a CSV of customer records. Columns are auto-detected and aligned to the trained model.")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        section("Data Preview")
        st.dataframe(df.head(8), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬡  Run AI Prediction"):
            loader = st.empty()
            for msg in [
                "⬡  Analysing data structure...",
                "⬡  Preprocessing features...",
                "⬡  Running Random Forest model...",
                "⬡  Applying risk classification...",
            ]:
                loader.markdown(f"<p class='nx-loader'>{msg}</p>", unsafe_allow_html=True)
                time.sleep(0.7)

            df, df_model = safe_prepare(df)
            preds = predictor.model.predict(df_model)
            probs = predictor.model.predict_proba(df_model)[:, 1]

            df["Prediction"] = preds
            df["Probability"] = probs
            df["RiskLevel"]   = df["Probability"].apply(churn_risk)
            loader.empty()
            st.session_state.df_result = df

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.df_result is not None:
        df = st.session_state.df_result

        divider()
        section("Summary Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Customers", f"{len(df):,}")
        c2.metric("Churn Rate",      f"{df['Prediction'].mean():.2%}")
        c3.metric("High Risk",       f"{len(df[df['RiskLevel']=='High Risk']):,}")
        c4.metric("Avg Probability", f"{df['Probability'].mean():.2f}")

        divider()
        section("Risk Analytics")

        ch1, ch2 = st.columns(2)

        # ── Donut chart ───────────────────────────────────────────────────────
        with ch1:
            risk_counts = df["RiskLevel"].value_counts().reset_index()
            risk_counts.columns = ["RiskLevel", "Count"]
            color_map = {"High Risk":"#dc2626","Medium Risk":"#d97706","Low Risk":"#059669"}

            fig = go.Figure(go.Pie(
                labels=risk_counts["RiskLevel"],
                values=risk_counts["Count"],
                hole=0.62,
                marker=dict(
                    colors=[color_map.get(r,"#4a4a58") for r in risk_counts["RiskLevel"]],
                    line=dict(color="#060608", width=2),
                ),
                textfont=dict(family="JetBrains Mono", size=10, color="white"),
                hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
            ))
            fig.update_layout(
                **plotly_dark(),
                title=dict(text="RISK BREAKDOWN", font=dict(size=10,family="JetBrains Mono"), x=0.02),
                showlegend=True,
                height=320,
                annotations=[dict(
                    text=f"<b>{len(df):,}</b><br><span style='font-size:9'>customers</span>",
                    x=0.5, y=0.5, font=dict(size=14,color="#f0f0f8",family="Bebas Neue"),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── Histogram ─────────────────────────────────────────────────────────
        with ch2:
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=df["Probability"], nbinsx=30,
                marker=dict(color="#dc2626", opacity=0.82,
                            line=dict(color="#060608", width=0.6)),
                hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
                name="",
            ))
            for x_val, label, color in [
                (0.3, "Low/Med", "#d97706"),
                (0.6, "Med/High", "#dc2626"),
            ]:
                fig.add_vline(
                    x=x_val, line_dash="dot", line_color=color, line_width=1.2,
                    annotation_text=label,
                    annotation_font=dict(family="JetBrains Mono", size=9, color=color),
                    annotation_position="top",
                )
            fig.update_layout(
                **plotly_dark(),
                title=dict(text="PROBABILITY DISTRIBUTION", font=dict(size=10,family="JetBrains Mono"), x=0.02),
                bargap=0.05, height=320, showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── Feature importance ─────────────────────────────────────────────────
        section("Feature Importance")
        try:
            imp    = predictor.model.feature_importances_
            imp_df = pd.DataFrame({
                "Feature":    predictor.features,
                "Importance": imp,
            }).sort_values("Importance", ascending=True).tail(10)

            fig = go.Figure(go.Bar(
                x=imp_df["Importance"],
                y=imp_df["Feature"],
                orientation="h",
                marker=dict(
                    color=imp_df["Importance"],
                    colorscale=[[0,"#1c1c22"],[0.4,"#7f1d1d"],[1,"#dc2626"]],
                    line=dict(color="#060608", width=0.5),
                ),
                hovertemplate="<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>",
            ))
            fig.update_layout(
                **plotly_dark(),
                title=dict(text="TOP 10 PREDICTIVE FEATURES", font=dict(size=10,family="JetBrains Mono"), x=0.02),
                height=340,
                yaxis=dict(gridcolor="transparent", tickfont=dict(size=10,family="JetBrains Mono")),
                xaxis=dict(tickfont=dict(size=9,family="JetBrains Mono")),
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.warning("Feature importance not available for this model.")

        # ── Retention strategies ───────────────────────────────────────────────
        divider()
        section("Retention Strategies · High-Risk Customers")

        high_risk = df[df["RiskLevel"] == "High Risk"].head(5)
        if high_risk.empty:
            empty_state("✓", "No High Risk Customers",
                        "All customers fall below the high-risk threshold with current settings.")
        else:
            for i, (idx, row) in enumerate(high_risk.iterrows()):
                prob_val = row.get("Probability", 0)
                bar_w    = int(prob_val * 100)
                st.markdown(f"""
<div class="cust-block">
  <div class="cust-hdr">
    <span class="cust-num">Customer {i+1:02d}</span>
    <div class="cust-sep"></div>
    <span class="cust-prob">{prob_val:.0%} RISK</span>
  </div>
  <div class="prog-track">
    <div class="prog-fill" style="width:{bar_w}%"></div>
  </div>
</div>""", unsafe_allow_html=True)
                tips = retention_strategy(row.to_dict(), "High Risk")
                for t in tips:
                    ret_card(t)
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ── AI Verdict ─────────────────────────────────────────────────────────
        divider()
        section("AI Verdict")
        avg_p = df["Probability"].mean()
        if avg_p < 0.6:
            st.markdown("""
<div class="nx-verdict verdict-ok">
  <span style="font-size:1.2rem">✓</span>
  READY FOR CLIENT · Churn risk within acceptable range
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="nx-verdict verdict-warn">
  <span style="font-size:1.2rem">⚠</span>
  REVIEW BEFORE SHARING · Elevated churn risk detected
</div>""", unsafe_allow_html=True)

        # ── Full table ─────────────────────────────────────────────────────────
        divider()
        section("Full Results Table")
        fc1, _, fc2 = st.columns([2, 5, 1.5])
        with fc1:
            filt = st.selectbox("Filter", ["All","High Risk","Medium Risk","Low Risk"],
                                label_visibility="collapsed")
        df_show = df if filt == "All" else df[df["RiskLevel"] == filt]
        st.dataframe(df_show, use_container_width=True)

        # ── Downloads ──────────────────────────────────────────────────────────
        divider()
        section("Export Reports")
        dl1, dl2, dl3 = st.columns([1, 1, 4])

        with dl1:
            # PDF: generate bytes → pass directly → no temp file
            pdf_bytes = generate_pdf(df)
            st.download_button(
                label="⬡  Download PDF Report",
                data=pdf_bytes,
                file_name="NEXUS_Retention_Report.pdf",
                mime="application/pdf",
            )

        with dl2:
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬡  Download CSV",
                data=csv,
                file_name="NEXUS_Predictions.csv",
                mime="text/csv",
            )


# ══════════════════════════════════════════════════════════════════════════════
# MANUAL
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "manual":

    st.markdown("<h2 style='margin-bottom:26px'>Manual Prediction</h2>", unsafe_allow_html=True)

    section("Upload Reference Dataset")
    uploaded_file = st.file_uploader("Drop CSV here", type=["csv"],
                                     label_visibility="collapsed", key="manual_up")

    if not uploaded_file:
        st.markdown("<br>", unsafe_allow_html=True)
        empty_state("⬡", "No Dataset Loaded",
                    "Upload a reference CSV so NEXUS can auto-generate input fields from your column types.")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        for col in df.columns:
            if "id" in col.lower():
                df = df.drop(columns=[col])
        if "Churn" in df.columns:
            df = df.drop(columns=["Churn"])

        section("Customer Attributes")
        input_data = {}
        cols = st.columns(3)
        for i, col in enumerate(df.columns):
            with cols[i % 3]:
                if df[col].dtype in ["int64", "float64"]:
                    input_data[col] = st.number_input(col, key=f"m_{col}")
                else:
                    opts = df[col].dropna().unique().tolist()
                    if len(opts) <= 8:
                        input_data[col] = st.selectbox(col, opts, key=f"m_{col}")
                    else:
                        input_data[col] = st.text_input(col, key=f"m_{col}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬡  Predict Churn Risk"):
            result = predictor.predict(input_data)

            if "error" in result:
                st.error(result["error"])
            else:
                prob  = result["probability"]
                level = churn_risk(prob)
                rcls  = risk_css(level)
                color = risk_color(level)
                bar_w = int(prob * 100)

                divider()
                section("Prediction Result")

                r1, r2 = st.columns([1, 2])
                with r1:
                    st.markdown(f"""
<div class="nx-risk-block">
  <p class="nx-risk-tag">Churn Probability</p>
  <p class="nx-risk-val {rcls}">{prob:.1%}</p>
  <div class="prog-track" style="margin-top:14px">
    <div class="prog-fill" style="width:{bar_w}%;background:{color}"></div>
  </div>
  <p class="nx-risk-tag" style="margin-top:20px">Risk Classification</p>
  <p class="nx-risk-val {rcls}" style="font-size:2rem">{level.upper()}</p>
</div>""", unsafe_allow_html=True)

                with r2:
                    fig = go.Figure(go.Indicator(
                        mode  = "gauge+number",
                        value = round(prob * 100, 1),
                        number= {"suffix":"%","font":{"size":46,"color":color,"family":"Bebas Neue"}},
                        gauge = {
                            "axis": {
                                "range":[0,100], "tickcolor":"#32323c", "tickwidth":1,
                                "tickfont":{"family":"JetBrains Mono","size":9,"color":"#4a4a58"},
                            },
                            "bar":{"color":color,"thickness":0.17},
                            "bgcolor":"#0c0c0f","borderwidth":0,
                            "steps":[
                                {"range":[0,30],  "color":"rgba(5,150,105,0.08)"},
                                {"range":[30,60], "color":"rgba(217,119,6,0.08)"},
                                {"range":[60,100],"color":"rgba(220,38,38,0.08)"},
                            ],
                            "threshold":{
                                "line":{"color":color,"width":2},
                                "thickness":0.85,"value":round(prob*100,1),
                            },
                        },
                    ))
                    fig.update_layout(
                        **plotly_dark(), height=240,
                        margin=dict(l=20,r=20,t=20,b=20),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                divider()
                section("Retention Recommendations")
                tips = retention_strategy(input_data, level)
                for t in tips:
                    ret_card(t)
