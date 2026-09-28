"""
UI Components & Brand Assets for BHARAT NIRIKSHAK — Powered by IBM
National Forensic Sciences University (NFSU) & Ministry of Home Affairs

Clean, professional IBM Carbon Design System:
- Top-Left: NFSU Logo & BHARAT NIRIKSHAK title
- Top-Right: IBM Logo & operational live status
- Clean corporate card styling (no neon/lightning/glow)
- 3-4s Interactive Welcome Toast & clean dismissable banner
- BOB AGENT AI Copilot (IBM Watsonx)
"""

import os
import base64
import textwrap
import streamlit as st
from datetime import datetime
from typing import Dict, Any

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

@st.cache_data
def get_logos_base64() -> Dict[str, str]:
    """Cache and return base64 data URIs for IBM and NFSU logos."""
    ibm_path = os.path.join(ASSETS_DIR, "ibm_logo.png")
    nfsu_path = os.path.join(ASSETS_DIR, "nfsu_logo.png")
    
    ibm_b64 = ""
    nfsu_b64 = ""
    
    if os.path.exists(ibm_path):
        with open(ibm_path, "rb") as f:
            ibm_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    if os.path.exists(nfsu_path):
        with open(nfsu_path, "rb") as f:
            nfsu_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
            
    return {"ibm": ibm_b64, "nfsu": nfsu_b64}


def get_global_css() -> str:
    """Return clean, professional IBM Carbon design styles with high contrast and no neon/glow."""
    return """
<style>
/* ── Clean Corporate IBM Enterprise Theme ── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.stApp {
    background-color: #0b111e;
    color: #f1f5f9;
}

.main .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1440px;
}

/* ── Corporate Cards (No glowing borders or text shadows) ── */
.corporate-card, .iciip-card {
    background-color: #111a2e;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
}

.metric-label-clean, .iciip-card-title {
    font-size: 0.78rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    margin-bottom: 4px;
}

.metric-value-clean, .iciip-card-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #38bdf8;
    line-height: 1.15;
}

.metric-sub-clean, .iciip-card-sub {
    font-size: 0.78rem;
    color: #cbd5e1;
    margin-top: 4px;
}

/* ── Top Header Bar (Logos in corners, Title on top left) ── */
.top-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 10px 20px;
    margin-bottom: 18px;
}

.logo-badge-container {
    background: #ffffff;
    padding: 4px 10px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 44px;
}

/* ── Welcome Banner Box ── */
.welcome-clean-box {
    background-color: #0f1c33;
    border: 1px solid #0f62fe;
    border-left: 5px solid #0f62fe;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 18px;
}

/* ── Legal Disclaimer Bar ── */
.disclaimer-bar {
    background-color: #1a1608;
    border: 1px solid #78350f;
    border-left: 4px solid #f59e0b;
    border-radius: 6px;
    padding: 10px 16px;
    margin-bottom: 16px;
    font-size: 0.8rem;
    color: #fde68a;
    line-height: 1.5;
}

/* ── Section Header ── */
.section-header {
    font-size: 1.1rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 18px 0 10px 0;
    border-left: 3px solid #0f62fe;
    padding-left: 10px;
}

/* ── Finding & Lead Items ── */
.finding-item {
    background: #0f1c33;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #cbd5e1;
}

/* ── Badges & Tags ── */
.iciip-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.74rem;
    font-weight: 700;
}

.badge-critical {
    background: #450a0a;
    color: #fca5a5;
    border: 1px solid #991b1b;
}

.badge-high {
    background: #431407;
    color: #fdba74;
    border: 1px solid #c2410c;
}

.badge-medium {
    background: #422006;
    color: #fde047;
    border: 1px solid #a16207;
}

.badge-low {
    background: #064e3b;
    color: #86efac;
    border: 1px solid #047857;
}

.tag-box {
    display: inline-block;
    background: #1e293b;
    color: #cbd5e1;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.72rem;
    margin: 2px;
}
</style>
"""


def render_brand_header(page_title: str, subtitle: str = "", badge_text: str = "● LIVE"):
    """
    Renders clean, minimal top header:
    - Top Left: NFSU Logo & BHARAT NIRIKSHAK title
    - Top Right: IBM Logo & operational live status badge
    No clutter, no heavy paragraphs, high visibility white background for logos.
    """
    logos = get_logos_base64()
    st.markdown(get_global_css(), unsafe_allow_html=True)
    
    nfsu_img_html = f'<div class="logo-badge-container"><img src="{logos["nfsu"]}" style="height:36px;max-width:130px;object-fit:contain;" alt="NFSU"></div>' if logos["nfsu"] else ''
    ibm_img_html = f'<div class="logo-badge-container"><img src="{logos["ibm"]}" style="height:24px;object-fit:contain;" alt="IBM"></div>' if logos["ibm"] else ''

    header_html = f"""<div class="top-header-bar">
    <div style="display:flex;align-items:center;gap:14px;">
        {nfsu_img_html}
        <div>
            <div style="font-size:1.45rem;font-weight:900;color:#ffffff;letter-spacing:0.5px;line-height:1.2;">
                BHARAT NIRIKSHAK
            </div>
            <div style="font-size:0.78rem;color:#38bdf8;font-weight:700;margin-top:2px;">
                Powered by IBM &nbsp;•&nbsp; <span style="color:#94a3b8;font-weight:400;">{page_title}</span>
            </div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:14px;">
        <span style="background:#0f62fe;color:#ffffff;padding:4px 12px;border-radius:4px;font-size:0.75rem;font-weight:700;letter-spacing:0.5px;">
            {badge_text}
        </span>
        {ibm_img_html}
    </div>
</div>"""
    
    st.markdown(header_html, unsafe_allow_html=True)


def render_welcome_popup():
    """
    Shows a clean 3-4 second welcome toast on initial visit.
    No intrusive text banners pushing content down.
    """
    if "welcome_seen" not in st.session_state:
        st.session_state.welcome_seen = True
        st.toast("👋 Welcome to BHARAT NIRIKSHAK — Powered by IBM", icon="🇮🇳")


def render_bob_agent(current_page_context: str = "Command Dashboard"):
    """
    Renders the persistent BOB AGENT (Powered by IBM) AI Assistant.
    Compact and non-intrusive by default.
    """
    from core.bob_agent import bob_agent
    
    st.markdown("---")
    
    if "bob_chat_history" not in st.session_state:
        st.session_state.bob_chat_history = [
            {
                "role": "assistant",
                "content": f"Hello Investigator! I am **BOB AGENT**, your embedded IBM Forensic AI Copilot. "
                           f"Ask me any question about Part 1 (DVI), Part 2 (Evidence), or Part 3 (Hotspots)!"
            }
        ]
        
    if "bob_panel_open" not in st.session_state:
        st.session_state.bob_panel_open = False

    # Header with toggle button
    top_col1, top_col2 = st.columns([4, 1.2])
    with top_col1:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.2rem;">🤖</span>
            <div>
                <b style="font-size:1rem;color:#ffffff;">BOB AGENT — IBM AI Forensic Copilot</b>
                <span style="color:#38bdf8;font-size:0.78rem;margin-left:8px;">Powered by IBM Watsonx</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with top_col2:
        btn_label = "🔼 Minimize Copilot" if st.session_state.bob_panel_open else "💬 Open BOB Copilot"
        if st.button(btn_label, key=f"toggle_bob_{current_page_context}", use_container_width=True):
            st.session_state.bob_panel_open = not st.session_state.bob_panel_open
            st.rerun()

    # Panel Body
    if st.session_state.bob_panel_open:
        panel_container = st.container()
        with panel_container:
            # Quick inquiry buttons
            st.caption("Quick Inquiries (1-Click Analysis):")
            q1, q2, q3, q4 = st.columns(4)
            
            clicked_query = None
            with q1:
                if st.button("🧬 How does DVI match?", key=f"bob_q1_{current_page_context}", use_container_width=True):
                    clicked_query = "How does Part 1 DVI scientific matching work?"
            with q2:
                if st.button("🔬 Evidence Prioritization", key=f"bob_q2_{current_page_context}", use_container_width=True):
                    clicked_query = "Explain Part 2 ISO/IEC 17025 3-pillar priority scoring"
            with q3:
                if st.button("🗺️ Moran's I Hotspots", key=f"bob_q3_{current_page_context}", use_container_width=True):
                    clicked_query = "How does Part 3 Moran's I and risk index work?"
            with q4:
                if st.button("📄 Form 27 Legal Manifest", key=f"bob_q4_{current_page_context}", use_container_width=True):
                    clicked_query = "How to issue an official FSL Form 27 manifest under Section 293 CrPC?"

            # If a quick question was clicked, handle it immediately
            if clicked_query:
                st.session_state.bob_chat_history.append({"role": "user", "content": clicked_query})
                reply = bob_agent.query(clicked_query, context=current_page_context)
                st.session_state.bob_chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

            # Display Chat History (last 6 messages)
            st.markdown('<div style="background:#0a1224;border:1px solid #1e293b;border-radius:8px;padding:12px 16px;margin:10px 0 14px 0;">', unsafe_allow_html=True)
            for msg in st.session_state.bob_chat_history[-6:]:
                if msg["role"] == "assistant":
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(msg["content"])
                else:
                    with st.chat_message("user", avatar="👮"):
                        st.markdown(msg["content"])
            st.markdown('</div>', unsafe_allow_html=True)

            # Chat Input Form
            with st.form(key=f"bob_chat_form_{current_page_context}"):
                user_input = st.text_input(
                    "Ask BOB Agent anything about this project:", 
                    placeholder="e.g. How does odontology dental charting match victims in Part 1?", 
                    label_visibility="collapsed"
                )
                fb_col1, fb_col2 = st.columns([1.5, 4])
                with fb_col1:
                    submitted = st.form_submit_button("💬 Ask BOB Agent", type="primary", use_container_width=True)
                with fb_col2:
                    clear_chat = st.form_submit_button("🗑️ Reset Chat", use_container_width=False)
                    
                if submitted and user_input:
                    st.session_state.bob_chat_history.append({"role": "user", "content": user_input})
                    reply = bob_agent.query(user_input, context=current_page_context)
                    st.session_state.bob_chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()

                if clear_chat:
                    st.session_state.bob_chat_history = [
                        {
                            "role": "assistant",
                            "content": f"Chat reset. I am ready to assist with **{current_page_context}** or any other forensic intelligence queries."
                        }
                    ]
                    st.rerun()
