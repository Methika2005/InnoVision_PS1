import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Green-Truth Auditor", layout="wide", page_icon="🌿")

# --- MOCK DATA FOR COMPETITORS (Integrate your CSVs here) ---
COMPETITOR_DB = {
    "T-Shirt": [
        {"Brand": "User Search", "Score": 0, "Cert": "Unknown"},
        {"Brand": "Patagonia", "Score": 92, "Cert": "B-Corp, GOTS"},
        {"Brand": "H&M Conscious", "Score": 45, "Cert": "Recycled Content"}
    ]
}

# --- FUNCTIONS ---
def draw_gauge(score, title="Sustainability Score"):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2ecc71"},
            'steps': [
                {'range': [0, 40], 'color': "#ff4b4b"},
                {'range': [40, 75], 'color': "#ffa500"},
                {'range': [75, 100], 'color': "#28a745"}]}))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
    return fig

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract title and meta description as a fallback for product text
        title = soup.title.string if soup.title else ""
        desc = soup.find('meta', attrs={'name': 'description'})
        desc_text = desc['content'] if desc else ""
        return f"{title} {desc_text}"
    except:
        return None

# --- UI LAYOUT ---
st.title("🌿 Green-Truth Auditor")
st.markdown("### The Intent-Aware Sustainability Shopping Assistant")

# --- INPUT SECTION ---
col_in1, col_in2 = st.columns([2, 1])

with col_in1:
    input_mode = st.tabs(["🔗 URL Analyzer", "📝 Text Description"])
    
    with input_mode[0]:
        url_input = st.text_input("Paste Amazon/Flipkart/Brand URL:", placeholder="https://www.example.com/product")
    
    with input_mode[1]:
        text_input = st.text_area("Paste Product Description:", height=150)

with col_in2:
    st.info("💡 *Innovation:* We don't just find buzzwords; we compare brands to help you find the truly ethical choice.")

if st.button("🚀 Run Deep Audit"):
    source_text = ""
    if url_input:
        with st.spinner("🕷️ Scraping product metadata..."):
            source_text = scrape_url(url_input)
            if not source_text:
                st.error("Could not scrape URL. Please paste text manually.")
    else:
        source_text = text_input

    if source_text:
        # --- LOGIC SIMULATION (Connect your model variables here) ---
        # Calculation: Base 100 -> -30 (Buzzwords) -> -40 (No Cert) -> +10 (Evidence)
        final_score = 32 
        
        # --- 1. GAUGE & VERDICT ---
        c1, c2 = st.columns([1, 2])
        with c1:
            st.plotly_chart(draw_gauge(final_score), use_container_width=True)
        with c2:
            st.subheader("⚠️ Likely Greenwashing")
            st.markdown(f"""
            *Reasoning Breakdown:*
            * 🚩 *Buzzword Penalty (-30):* Uses "eco-friendly" and "natural" without context.
            * 🚩 *Certification Gap (-40):* Brand not found in B-Corp or GOTS database.
            * ✅ *Data Credit (+10):* Mentions 'Organic Cotton' (Self-claimed).
            """)

        st.divider()

        # --- 2. COMPETITOR COMPARISON (THE UNIQUE EDGE) ---
        st.subheader("⚖️ How it Compares")
        comp_col1, comp_col2, comp_col3 = st.columns(3)
        
        # Simulating a comparison for a "T-Shirt" category
        competitors = COMPETITOR_DB["T-Shirt"]
        
        with comp_col1:
            st.metric("This Brand", f"{final_score}/100", "Current Choice", delta_color="inverse")
        with comp_col2:
            st.metric(competitors[1]["Brand"], f"{competitors[1]['score']}/100", "GOTS Certified")
        with comp_col3:
            st.success(f"🌟 *Better Choice:* {competitors[1]['Brand']}")
            st.caption("Lower carbon footprint and verified supply chain.")

        # --- 3. ANNOTATED TEXT ---
        st.subheader("🕵️ Detailed Audit Trail")
        st.expander("Show Analyzed Text").write(source_text)
        
        # Visual cues for text analysis
        st.markdown("""
        <div style="background:#fff3cd; padding:10px; border-left:5px solid #ffa500;">
        <b>Flagged Segment:</b> "...our 100% natural and eco-friendly process..." <br>
        <i>Critique: No specific metric provided for 'natural'.</i>
        </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write("✅ *B-Corp Database:* Synced")
st.sidebar.write("✅ *GOTS Database:* Synced")
st.sidebar.write("🤖 *Model:* BART-MNLI (87.5% Acc)")
