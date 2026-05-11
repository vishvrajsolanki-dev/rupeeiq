# app.py — RupeeIQ | Bloomberg Terminal x Indian Street Poster
# Run with: streamlit run app.py

import io
import time
import streamlit as st
import streamlit.components.v1 as components

from utils.data_loader            import load_csv, get_summary
from utils.preprocessor           import preprocess, get_spending_profile, get_daily_spending
from modules.personality_profiler import get_personality, build_radar_chart, build_bar_chart
from modules.crisis_predictor     import predict_crisis, build_crisis_chart
from modules.story_narrator       import get_story

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="RupeeIQ",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION STATE DEFAULTS ────────────────────────────────────
if "page"           not in st.session_state: st.session_state.page           = "HOME"
if "file_bytes"     not in st.session_state: st.session_state.file_bytes     = None
if "file_name"      not in st.session_state: st.session_state.file_name      = None
if "analysis"       not in st.session_state: st.session_state.analysis       = None

# ── GLOBAL CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&family=Bebas+Neue&family=DM+Sans:wght@300;400;500;700&display=swap');

:root {
    --black:   #05080A;
    --dark1:   #0B0F13;
    --dark2:   #111820;
    --dark3:   #182028;
    --acid:    #C8FF00;
    --acid2:   #00FFB2;
    --amber:   #FFB300;
    --red:     #FF3B3B;
    --blue:    #3D8BFF;
    --muted:   #3D5060;
    --label:   #7A9AAA;
    --text:    #D8E4EE;
    --mono:    'IBM Plex Mono', monospace;
    --display: 'Bebas Neue', sans-serif;
    --body:    'DM Sans', sans-serif;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"] {
    background-color: var(--black) !important;
    color: var(--text) !important;
    font-family: var(--body) !important;
}

[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,0,0,0.07) 2px, rgba(0,0,0,0.07) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

.main .block-container {
    max-width: 1140px !important;
    padding: 1rem 1.75rem 5rem !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
.stDeployButton { display: none !important; }

/* ── SIDEBAR ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: var(--dark1) !important;
    border-right: 1px solid var(--dark3) !important;
}
[data-testid="stSidebarContent"] { padding: 1.5rem 1.25rem !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: var(--text) !important; }

/* FIX: iframes must not capture clicks */
[data-testid="stSidebar"] iframe { pointer-events: none !important; }

/* ── NAV BUTTONS — invisible click layer over visual cards ── */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    opacity: 0 !important;
    height: 52px !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    position: relative !important;
    top: -52px !important;
    margin-bottom: -52px !important;
    z-index: 999 !important;
    cursor: pointer !important;
}

/* ── FILE UPLOADER ────────────────────────────────────────── */
[data-testid="stFileUploader"] { background: var(--dark1) !important; }
[data-testid="stFileUploader"] > label { display: none !important; }
[data-testid="stFileUploaderDropzone"] {
    background: var(--dark1) !important;
    border: 1px dashed var(--acid) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] div,
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] p {
    color: var(--muted) !important;
    font-family: var(--mono) !important;
    font-size: 0.62rem !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: transparent !important;
    border: 1px solid var(--dark3) !important;
    color: var(--label) !important;
    font-family: var(--mono) !important;
    font-size: 0.62rem !important;
    border-radius: 4px !important;
    padding: 0.3rem 0.75rem !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    border-color: var(--acid) !important;
    color: var(--acid) !important;
}
[data-testid="stFileUploaderFile"] {
    background: var(--dark2) !important;
    border: 1px solid var(--dark3) !important;
    border-radius: 4px !important;
}
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] p {
    color: var(--label) !important;
    font-family: var(--mono) !important;
    font-size: 0.62rem !important;
}

/* ── METRICS ──────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--dark2) !important;
    border: 1px solid var(--dark3) !important;
    border-top: 2px solid var(--acid) !important;
    border-radius: 6px !important;
    padding: 1rem 1.1rem !important;
}
[data-testid="stMetricLabel"] p {
    font-family: var(--mono) !important;
    font-size: 0.58rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: var(--label) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    color: var(--acid) !important;
    font-size: 1.25rem !important;
}

/* ── DOWNLOAD BUTTON ──────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
    background: transparent !important;
    border: 1px solid var(--dark3) !important;
    color: var(--label) !important;
    font-family: var(--mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    border-radius: 4px !important;
    width: 100% !important;
    padding: 0.5rem !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: var(--acid) !important;
    color: var(--acid) !important;
    background: rgba(200,255,0,0.04) !important;
}

/* ── ALERTS ───────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 6px !important;
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span { color: inherit !important; font-family: var(--mono) !important; }

/* ── PROGRESS ─────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--acid), var(--acid2)) !important;
    border-radius: 2px !important;
}

/* ── PLOTLY ───────────────────────────────────────────────── */
.js-plotly-plot .plotly .modebar { background: transparent !important; }
.js-plotly-plot .plotly .modebar-btn path { fill: var(--muted) !important; }

/* ── SCROLLBAR ────────────────────────────────────────────── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--black); }
::-webkit-scrollbar-thumb { background: var(--dark3); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--acid); }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Bebas+Neue&display=swap" rel="stylesheet">
    <div style="padding:0.25rem 0 1.5rem;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                    letter-spacing:5px;color:#3D5060;margin-bottom:0.3rem;">FINANCE INTELLIGENCE</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.8rem;
                    color:#C8FF00;letter-spacing:3px;line-height:1;
                    text-shadow:0 0 30px rgba(200,255,0,0.25);">
            RUPEE<span style="color:#00FFB2;">IQ</span></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
                    color:#4A6070;margin-top:0.5rem;letter-spacing:1px;">
            Know Your Money. Know Yourself.</div>
        <div style="display:flex;gap:4px;margin-top:1rem;">
            <div style="width:30px;height:2px;background:#C8FF00;box-shadow:0 0 8px #C8FF00;"></div>
            <div style="width:10px;height:2px;background:#00FFB2;"></div>
            <div style="width:4px;height:2px;background:#3D5060;"></div>
        </div>
    </div>
    """, height=145)

    st.markdown(
        "<div style='font-family:IBM Plex Mono,monospace;font-size:0.52rem;"
        "letter-spacing:4px;color:#3A5060;margin-bottom:0.5rem;'>NAVIGATE</div>",
        unsafe_allow_html=True
    )

    current_page = st.session_state.page

    def nav_card(icon, label, page_key, accent, module_tag):
        is_active  = current_page == page_key
        bg         = "#111820" if is_active else "#0D1318"
        border     = accent if is_active else "#182028"
        text_color = accent if is_active else "#7A9AAA"
        tag_color  = accent if is_active else "#3D5060"
        fw         = "700" if is_active else "400"

        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
        <div style="background:{bg};border:1px solid {border};border-left:3px solid {border};
                    border-radius:6px;padding:0.65rem 0.85rem;pointer-events:none;margin-bottom:2px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;align-items:center;gap:0.5rem;">
                    <span style="font-size:0.9rem;">{icon}</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.63rem;
                                 letter-spacing:2px;color:{text_color};font-weight:{fw};">
                        {label}</span>
                </div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.46rem;
                             letter-spacing:1px;color:{tag_color};padding:2px 5px;
                             border:1px solid {tag_color};border-radius:3px;">{module_tag}</span>
            </div>
        </div>
        """, height=50)

        if st.button(label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.page = page_key
            st.rerun()

    nav_card("🏠", "HOME",         "HOME",         "#C8FF00", "DASH")
    nav_card("🧠", "PERSONALITY",  "PERSONALITY",  "#C8FF00", "M01")
    nav_card("🚨", "CRISIS RADAR", "CRISIS RADAR", "#FFB300", "M02")
    nav_card("📖", "MONEY STORY",  "MONEY STORY",  "#3D8BFF", "M03")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-family:IBM Plex Mono,monospace;font-size:0.52rem;"
        "letter-spacing:4px;color:#3A5060;margin-bottom:0.5rem;'>UPLOAD DATA</div>",
        unsafe_allow_html=True
    )

    # ── FILE UPLOADER — store BYTES immediately, not the file object ──
    # Bytes survive page reruns; file objects do not.
    uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        new_bytes = uploaded_file.getvalue()
        new_name  = uploaded_file.name
        if new_name != st.session_state.file_name:
            st.session_state.file_bytes = new_bytes
            st.session_state.file_name  = new_name
            st.session_state.analysis   = None

    try:
        with open("data/sample_transactions.csv", "rb") as f:
            st.download_button(
                label="↓  SAMPLE CSV",
                data=f,
                file_name="sample_transactions.csv",
                mime="text/csv",
                use_container_width=True
            )
    except FileNotFoundError:
        pass

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&display=swap" rel="stylesheet">
    <div style="border-top:1px solid #182028;padding-top:1rem;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
                    color:#2A3D4A;letter-spacing:1px;line-height:2.2;">
            RupeeIQ v1.0<br>3 Modules Active<br>M1 · M2 · M3 ✓</div>
    </div>
    """, height=80)


# ── CURRENT PAGE ──────────────────────────────────────────────
page         = st.session_state.page
has_file     = st.session_state.file_bytes is not None
has_analysis = st.session_state.analysis   is not None


# ── CACHED ANALYSIS ───────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_analysis(file_bytes, filename):
    file_obj         = io.BytesIO(file_bytes)
    file_obj.name    = filename
    df, error        = load_csv(file_obj)
    if error:
        return None, error
    df               = preprocess(df)
    spending_profile = get_spending_profile(df)
    personality      = get_personality(spending_profile)
    daily_df         = get_daily_spending(df)
    summary          = get_summary(df)
    current_balance  = float(df["balance"].iloc[-1])
    crisis           = predict_crisis(daily_df, current_balance)
    story            = get_story(df, spending_profile, crisis, personality["name"])
    return {
        "spending_profile": spending_profile,
        "personality":      personality,
        "crisis":           crisis,
        "story":            story,
        "summary":          summary,
        "current_balance":  current_balance,
    }, None


# ── RUN ANALYSIS ONCE — results live in session_state.analysis ─
if has_file and not has_analysis:
    progress_bar = st.progress(0)
    status       = st.empty()

    def set_status(pct, msg):
        progress_bar.progress(pct)
        status.markdown(
            f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
            f"color:#7A9AAA;letter-spacing:2px;padding:0.2rem 0;'>"
            f"<span style='color:#C8FF00;'>▶</span>&nbsp;{msg}</div>",
            unsafe_allow_html=True
        )

    set_status(20, "LOADING & PREPROCESSING...")
    time.sleep(0.1)
    set_status(55, "RUNNING ALL 3 MODULES...")

    results, error = run_analysis(
        st.session_state.file_bytes,
        st.session_state.file_name
    )

    if error:
        st.error(f"❌ {error}")
        st.stop()

    st.session_state.analysis = results
    has_analysis = True

    set_status(100, "ANALYSIS COMPLETE")
    time.sleep(0.25)
    progress_bar.empty()
    status.empty()


# ── HELPERS ───────────────────────────────────────────────────
def dark_chart(fig):
    fig.update_layout(
        paper_bgcolor="#05080A", plot_bgcolor="#0B0F13",
        font=dict(family="IBM Plex Mono, monospace", color="#7A9AAA", size=10),
        xaxis=dict(gridcolor="#182028", zerolinecolor="#182028",
                   tickfont=dict(color="#7A9AAA"), linecolor="#182028"),
        yaxis=dict(gridcolor="#182028", zerolinecolor="#182028",
                   tickfont=dict(color="#7A9AAA"), linecolor="#182028"),
        margin=dict(l=40, r=20, t=45, b=35),
        title_font=dict(family="IBM Plex Mono, monospace", color="#D8E4EE", size=12),
    )
    return fig

def get_archetype_icon(name):
    n = name.lower()
    if "disciplined" in n or "saver"   in n: return "💎"
    if "impulsive"   in n or "spender" in n: return "🔥"
    if "foodie"      in n:                   return "🍜"
    if "social"      in n:                   return "🎉"
    if "balanced"    in n:                   return "⚖️"
    return "💰"

def show_upload_prompt(module_name, accent):
    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Bebas+Neue&display=swap" rel="stylesheet">
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:340px;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1.5rem;">📂</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                    color:{accent};letter-spacing:3px;margin-bottom:0.75rem;">{module_name}</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                    color:#4A6070;letter-spacing:2px;line-height:2;">
            Upload a transaction CSV from the sidebar<br>to unlock this module.</div>
    </div>
    """, height=360)

def show_landing():
    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Bebas+Neue&family=DM+Sans:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        @keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
        @keyframes fadeUp{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:translateY(0);}}
        .card{animation:fadeUp 0.5s ease forwards;opacity:0;}
        .card:nth-child(1){animation-delay:0.1s;}
        .card:nth-child(2){animation-delay:0.22s;}
        .card:nth-child(3){animation-delay:0.34s;}
    </style>
    <div style="padding:2.5rem 0 1rem;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
                    letter-spacing:5px;color:#4A6070;margin-bottom:0.5rem;">
            PERSONAL FINANCE INTELLIGENCE SYSTEM</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5.5rem;
                    color:#C8FF00;letter-spacing:4px;line-height:0.9;
                    text-shadow:0 0 60px rgba(200,255,0,0.12);">
            RUPEE<span style="color:#00FFB2;">IQ</span></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
                    color:#4A6070;margin-top:1rem;letter-spacing:1px;">
            <span style="color:#C8FF00;">▶</span>&nbsp;
            Upload your transaction CSV from the sidebar to begin
            <span style="animation:blink 1s infinite;display:inline-block;">_</span></div>
    </div>
    <div style="margin-top:2rem;display:grid;grid-template-columns:repeat(3,1fr);
                gap:1px;background:#182028;border:1px solid #182028;
                border-radius:8px;overflow:hidden;">
        <div class="card" style="background:#0B0F13;padding:1.75rem 1.5rem;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;color:#C8FF00;line-height:1;">01</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;
                        letter-spacing:3px;color:#4A6070;margin:0.4rem 0 0.75rem;">MODULE</div>
            <div style="font-family:'DM Sans',sans-serif;font-size:1.05rem;
                        font-weight:700;color:#D8E4EE;margin-bottom:0.4rem;">Financial Personality</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;
                        color:#4A6070;line-height:1.8;">5 archetypes.<br>Distance-based<br>clustering engine.</div>
        </div>
        <div class="card" style="background:#0B0F13;padding:1.75rem 1.5rem;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;color:#FFB300;line-height:1;">02</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;
                        letter-spacing:3px;color:#4A6070;margin:0.4rem 0 0.75rem;">MODULE</div>
            <div style="font-family:'DM Sans',sans-serif;font-size:1.05rem;
                        font-weight:700;color:#D8E4EE;margin-bottom:0.4rem;">Crisis Radar</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;
                        color:#4A6070;line-height:1.8;">Burn rate forecast.<br>Linear regression<br>crisis prediction.</div>
        </div>
        <div class="card" style="background:#0B0F13;padding:1.75rem 1.5rem;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;color:#3D8BFF;line-height:1;">03</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;
                        letter-spacing:3px;color:#4A6070;margin:0.4rem 0 0.75rem;">MODULE</div>
            <div style="font-family:'DM Sans',sans-serif;font-size:1.05rem;
                        font-weight:700;color:#D8E4EE;margin-bottom:0.4rem;">Money Story</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;
                        color:#4A6070;line-height:1.8;">Pattern detection.<br>Rule-based NLP<br>narrative engine.</div>
        </div>
    </div>
    <div style="background:#0D1117;border:1px solid #182028;border-top:none;
                border-radius:0 0 8px 8px;padding:0.7rem 1.5rem;
                display:flex;align-items:center;gap:0.75rem;">
        <div style="width:6px;height:6px;border-radius:50%;background:#C8FF00;
                    box-shadow:0 0 6px #C8FF00;animation:blink 2s infinite;"></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
                    color:#4A6070;letter-spacing:1px;">SYSTEM READY — AWAITING INPUT</div>
    </div>
    """, height=540)


# ════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════
if page == "HOME":
    if not has_analysis:
        show_landing()
    else:
        r               = st.session_state.analysis
        personality     = r["personality"]
        crisis          = r["crisis"]
        story           = r["story"]
        summary         = r["summary"]
        current_balance = r["current_balance"]
        arch_icon       = get_archetype_icon(personality["name"])
        arch_name       = personality["name"]
        safe            = crisis["is_safe"]
        days            = crisis["days_remaining"]
        burn            = crisis["avg_daily_spend"]
        opening         = story["opening"]
        sc              = "#C8FF00" if safe else "#FF3B3B"
        sl              = "STABLE" if safe else "ALERT"
        crisis_msg      = ("Balance is sustainable. Keep current spending patterns."
                           if safe else
                           f"Balance depletes in {days} day(s). Reduce daily burn immediately.")

        components.html("""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                    letter-spacing:4px;color:#4A6070;margin-bottom:0.6rem;">─── FINANCIAL SNAPSHOT</div>
        """, height=28)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TRANSACTIONS", summary["total_transactions"])
        c2.metric("TOTAL SPENT",  f'Rs.{summary["total_spent"]:,.0f}')
        c3.metric("TOTAL SAVED",  f'Rs.{summary["total_saved"]:,.0f}')
        c4.metric("TOP CATEGORY", summary["top_category"])
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Bebas+Neue&family=DM+Sans:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            @keyframes fadeUp{{from{{opacity:0;transform:translateY(14px);}}to{{opacity:1;transform:translateY(0);}}}}
            .hb{{animation:fadeUp 0.4s ease forwards;opacity:0;}}
            .hb:nth-child(1){{animation-delay:0.05s;}}
            .hb:nth-child(2){{animation-delay:0.15s;}}
            .hb:nth-child(3){{animation-delay:0.25s;}}
        </style>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;
                    background:#182028;border-radius:8px;overflow:hidden;margin-bottom:1px;">
            <div class="hb" style="background:#0B0F13;padding:1.75rem;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                            letter-spacing:4px;color:#4A6070;margin-bottom:1rem;">ARCHETYPE DETECTED</div>
                <div style="display:flex;align-items:flex-start;gap:1rem;">
                    <div style="font-size:2.5rem;line-height:1;flex-shrink:0;">{arch_icon}</div>
                    <div>
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.9rem;
                                    color:#C8FF00;letter-spacing:3px;line-height:1.05;
                                    text-shadow:0 0 20px rgba(200,255,0,0.2);">{arch_name}</div>
                        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.63rem;
                                    color:#7A9AAA;margin-top:0.5rem;line-height:1.7;">
                            {personality['desc'][:110]}...</div>
                    </div>
                </div>
                <div style="margin-top:1.25rem;padding:0.875rem;background:#111820;
                            border-left:2px solid #FFB300;border-radius:0 6px 6px 0;">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                                letter-spacing:2px;color:#FFB300;margin-bottom:0.3rem;">TIP</div>
                    <div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                                color:#C8D8E8;line-height:1.6;">{personality['tip']}</div>
                </div>
            </div>
            <div class="hb" style="background:#0B0F13;padding:1.75rem;border-left:1px solid #182028;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                            letter-spacing:4px;color:#4A6070;margin-bottom:1rem;">CRISIS STATUS</div>
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.75rem;">
                    <div style="width:8px;height:8px;border-radius:50%;
                                background:{sc};box-shadow:0 0 8px {sc};"></div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;
                                color:{sc};letter-spacing:3px;">{sl}</div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1rem;">
                    <div style="background:#111820;border-radius:6px;padding:0.875rem;">
                        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
                                    letter-spacing:2px;color:#4A6070;margin-bottom:0.25rem;">DAYS LEFT</div>
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                                    color:#C8FF00;letter-spacing:2px;">{days}</div>
                    </div>
                    <div style="background:#111820;border-radius:6px;padding:0.875rem;">
                        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
                                    letter-spacing:2px;color:#4A6070;margin-bottom:0.25rem;">DAILY BURN</div>
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.7rem;
                                    color:#FFB300;letter-spacing:1px;">Rs.{burn:,.0f}</div>
                    </div>
                </div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.63rem;
                            color:#9BAABB;line-height:1.7;">{crisis_msg}</div>
            </div>
        </div>
        <div class="hb" style="background:#0B0F13;border:1px solid #182028;border-top:none;
                    border-radius:0 0 8px 8px;border-left:3px solid #3D8BFF;padding:1.5rem;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                        letter-spacing:4px;color:#3D8BFF;margin-bottom:0.75rem;">YOUR MONEY STORY</div>
            <div style="font-family:'DM Sans',sans-serif;font-size:1.05rem;
                        font-weight:300;color:#D8E4EE;line-height:1.8;font-style:italic;">
                "{opening}"</div>
        </div>
        """, height=510)


# ════════════════════════════════════════════════════════════
# PAGE: PERSONALITY
# ════════════════════════════════════════════════════════════
elif page == "PERSONALITY":
    if not has_analysis:
        show_upload_prompt("PERSONALITY PROFILER", "#C8FF00")
    else:
        r           = st.session_state.analysis
        personality = r["personality"]
        arch_icon   = get_archetype_icon(personality["name"])
        arch_name   = personality["name"]

        components.html("""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                    letter-spacing:4px;color:#4A6070;margin-bottom:1rem;">
            ─── MODULE 01 / FINANCIAL PERSONALITY PROFILER</div>
        """, height=28)

        col_l, col_r = st.columns([1, 1.8])
        with col_l:
            components.html(f"""
            <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Bebas+Neue&family=DM+Sans:wght@400;700&display=swap" rel="stylesheet">
            <div style="background:#0B0F13;border:1px solid #182028;
                        border-left:3px solid #C8FF00;border-radius:8px;padding:1.75rem;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                            letter-spacing:4px;color:#4A6070;margin-bottom:1rem;">ARCHETYPE DETECTED</div>
                <div style="font-size:3rem;margin-bottom:0.6rem;line-height:1;">{arch_icon}</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                            color:#C8FF00;letter-spacing:3px;line-height:1.05;margin-bottom:1rem;
                            text-shadow:0 0 20px rgba(200,255,0,0.2);">{arch_name}</div>
                <p style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                          color:#9BAABB;line-height:1.8;margin-bottom:1.5rem;">{personality['desc']}</p>
                <div style="background:#111820;border-radius:6px;padding:1rem;border-left:2px solid #FFB300;">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                                letter-spacing:3px;color:#FFB300;margin-bottom:0.4rem;">RUPEEIQ TIP</div>
                    <div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                                color:#C8D8E8;line-height:1.6;">{personality['tip']}</div>
                </div>
            </div>
            """, height=480)

        with col_r:
            radar = build_radar_chart(personality)
            dark_chart(radar)
            radar.update_layout(polar=dict(
                bgcolor="#0B0F13",
                radialaxis=dict(gridcolor="#182028", tickfont=dict(color="#4A6070", size=9)),
                angularaxis=dict(gridcolor="#182028", tickfont=dict(color="#9BAABB", size=10)),
            ))
            st.plotly_chart(radar, use_container_width=True)

        bar = build_bar_chart(personality)
        dark_chart(bar)
        bar.update_traces(marker_color="#C8FF00", opacity=0.8)
        bar.update_layout(title="Spending Distribution vs Archetype Centers")
        st.plotly_chart(bar, use_container_width=True)


# ════════════════════════════════════════════════════════════
# PAGE: CRISIS RADAR
# ════════════════════════════════════════════════════════════
elif page == "CRISIS RADAR":
    if not has_analysis:
        show_upload_prompt("CRISIS RADAR", "#FFB300")
    else:
        r               = st.session_state.analysis
        crisis          = r["crisis"]
        current_balance = r["current_balance"]

        components.html("""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                    letter-spacing:4px;color:#4A6070;margin-bottom:1rem;">
            ─── MODULE 02 / BUDGET CRISIS PREDICTOR</div>
        """, height=28)

        if crisis["is_safe"]:
            st.success("✅  BALANCE STABLE — No immediate crisis detected.")
        else:
            st.error(f"🚨  CRISIS DETECTED — Balance depletes in {crisis['days_remaining']} day(s). Take action now.")

        m1, m2, m3 = st.columns(3)
        m1.metric("CURRENT BALANCE", f'Rs.{current_balance:,.0f}')
        m2.metric("AVG DAILY BURN",  f'Rs.{crisis["avg_daily_spend"]:,.0f}')
        m3.metric("DAYS REMAINING",  crisis["days_remaining"])
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        fig = build_crisis_chart(crisis)
        dark_chart(fig)
        fig.update_traces(selector=dict(mode="lines"), line=dict(width=2))
        st.plotly_chart(fig, use_container_width=True)

        components.html("""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                    letter-spacing:4px;color:#4A6070;margin:0.5rem 0 0.6rem;">─── RECOVERY PLAN</div>
        """, height=28)

        for tip in crisis["recovery_plan"]:
            st.markdown(
                f"<div style='background:#0B0F13;border:1px solid #182028;"
                f"border-left:2px solid #FFB300;border-radius:0 6px 6px 0;"
                f"padding:0.75rem 1rem;font-family:IBM Plex Mono,monospace;"
                f"font-size:0.72rem;color:#9BAABB;margin-bottom:0.4rem;line-height:1.6;'>{tip}</div>",
                unsafe_allow_html=True
            )


# ════════════════════════════════════════════════════════════
# PAGE: MONEY STORY
# ════════════════════════════════════════════════════════════
elif page == "MONEY STORY":
    if not has_analysis:
        show_upload_prompt("MONEY STORY", "#3D8BFF")
    else:
        r     = st.session_state.analysis
        story = r["story"]

        components.html("""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                    letter-spacing:4px;color:#4A6070;margin-bottom:1rem;">
            ─── MODULE 03 / MONEY STORY NARRATOR</div>
        """, height=28)

        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=DM+Sans:wght@300;400;700&display=swap" rel="stylesheet">
        <div style="border-left:3px solid #3D8BFF;padding:1.5rem 2rem;
                    background:#09101A;border-radius:0 10px 10px 0;margin-bottom:0.5rem;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                        letter-spacing:4px;color:#3D8BFF;margin-bottom:0.75rem;">OPENING</div>
            <div style="font-family:'DM Sans',sans-serif;font-size:1.1rem;
                        font-weight:300;color:#D8E4EE;line-height:1.8;font-style:italic;">
                "{story['opening']}"</div>
        </div>
        """, height=130)

        components.html("""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                    letter-spacing:4px;color:#4A6070;margin:0.75rem 0 0.6rem;">─── PATTERNS DETECTED</div>
        """, height=28)

        for line in story["patterns"]:
            st.markdown(
                f"<div style='background:#0B0F13;border:1px solid #182028;"
                f"border-radius:6px;padding:0.875rem 1.1rem;"
                f"font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
                f"color:#9BAABB;line-height:1.7;margin-bottom:0.4rem;'>{line}</div>",
                unsafe_allow_html=True
            )

        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=DM+Sans:wght@300;400&display=swap" rel="stylesheet">
        <div style="margin-top:0.75rem;background:#0B0F13;border:1px solid #182028;
                    border-top:2px solid #3D8BFF;border-radius:8px;padding:1.5rem;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
                        letter-spacing:4px;color:#3D8BFF;margin-bottom:0.6rem;">VERDICT</div>
            <div style="font-family:'DM Sans',sans-serif;font-size:0.95rem;
                        font-weight:400;color:#D8E4EE;line-height:1.8;">{story['closing']}</div>
        </div>
        """, height=155)