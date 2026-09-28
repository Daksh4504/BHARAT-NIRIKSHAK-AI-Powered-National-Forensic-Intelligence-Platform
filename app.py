"""
BHARAT NIRIKSHAK — Powered by IBM
National Forensic Sciences University (NFSU) & Ministry of Home Affairs

Integrates:
- Part 1: DVI Forensic Intelligence (Interpol Odontology, DNA, Surgical, Tattoos)
- Part 2: AI Crime Scene Evidence Prioritization (ISO/IEC 17025, 3-Pillar Scoring, Form 27)
- Part 3: Predictive Crime Hotspot Mapping (Ahmedabad Spatio-Temporal Panel, Moran's I)
- BOB AGENT: Embedded IBM Watsonx AI Forensic Copilot
"""

import streamlit as st
from core.mock_data import CASES, CASES_BY_ID
from core.dvi_engine import dvi_engine
from core.evidence_engine import evidence_engine
from core.ui_components import get_logos_base64, get_global_css, render_bob_agent

st.set_page_config(
    page_title="BHARAT NIRIKSHAK — Powered by IBM",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Global Enterprise CSS with IBM Carbon Design System (No Glow) ──
st.markdown(get_global_css(), unsafe_allow_html=True)

# ── Navigation ───────────────────────────────────────────────────────
pages = st.navigation([
    st.Page("pages/dashboard.py",       title="Command Dashboard",          icon="🏠"),
    st.Page("pages/dvi.py",              title="Part 1: DVI Intelligence",    icon="🆔"),
    st.Page("pages/evidence_triage.py",  title="Part 2: Evidence Triage",    icon="🔬"),
    st.Page("pages/crime_hotspot.py",    title="Part 3: Crime Hotspot Map",  icon="🗺️"),
    st.Page("pages/cases.py",            title="Case Registry",              icon="📁"),
    st.Page("pages/fir_intelligence.py", title="FIR NLP Intelligence",       icon="📄"),
    st.Page("pages/deepfake.py",         title="Deepfake Media Lab",         icon="🎭"),
    st.Page("pages/reports.py",          title="Investigation Dossiers",     icon="📊"),
    st.Page("pages/presentation.py",     title="Executive Presentation (7 Slides)", icon="📽️"),
])

# ── Sidebar Branding & Controls ──────────────────────────────────────
with st.sidebar:
    logos = get_logos_base64()
    
    # Dual Logo Container (NFSU on left, IBM on right) — Clean Visible Pills
    st.markdown(f"""
    <div style="background:#0f172a; border:1px solid #1e293b; border-radius:8px; padding:12px; margin-bottom:12px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
            <div style="background:#ffffff; padding:2px 8px; border-radius:4px; display:inline-flex; align-items:center;">
                {'<img src="' + logos['nfsu'] + '" style="height:30px;max-width:105px;object-fit:contain;" alt="NFSU">' if logos['nfsu'] else ''}
            </div>
            <div style="background:#ffffff; padding:2px 8px; border-radius:4px; display:inline-flex; align-items:center;">
                {'<img src="' + logos['ibm'] + '" style="height:20px;object-fit:contain;" alt="IBM">' if logos['ibm'] else ''}
            </div>
        </div>
        <div style="border-top:1px solid #1e293b; padding-top:8px;">
            <div style="font-size:1.15rem; font-weight:900; color:#ffffff; letter-spacing:0.5px; line-height:1.2;">
                BHARAT NIRIKSHAK
            </div>
            <div style="font-size:0.75rem; color:#38bdf8; font-weight:700; margin-top:2px;">
                POWERED BY IBM
            </div>
            <div style="font-size:0.65rem; color:#94a3b8; margin-top:1px;">
                National Forensic Sciences University • MHA
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Active Case Context ──────────────────────────────────────────
    if "active_case_id" not in st.session_state:
        st.session_state.active_case_id = CASES[0]["case_id"]

    st.markdown("**🔗 Active Case Context**")
    case_labels = [f"{c['case_id']} — {c['title'][:24]}" for c in CASES]
    case_ids    = [c["case_id"] for c in CASES]

    current_idx = case_ids.index(st.session_state.active_case_id) if st.session_state.active_case_id in case_ids else 0
    chosen_label = st.selectbox("Switch Case", case_labels, index=current_idx, label_visibility="collapsed")
    st.session_state.active_case_id = case_ids[case_labels.index(chosen_label)]

    active = CASES_BY_ID.get(st.session_state.active_case_id, CASES[0])
    p_col = {"Critical":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#22c55e"}.get(active["priority"],"#94a3b8")
    st.markdown(f"""
    <div style="background:#0a1628; border:1px solid #1e3a5f; border-radius:8px; padding:10px; margin-top:4px; font-size:0.79rem; border-left:3px solid {p_col};">
        <div style="color:#11d3f3; font-weight:800; margin-bottom:2px;">{active['case_id']}</div>
        <div style="color:{p_col}; font-weight:700; font-size:0.74rem;">{active['priority']} Priority</div>
        <div style="color:#94a3b8; margin-top:3px;">{active['crime_type']}</div>
        <div style="color:#64748b; margin-top:3px; font-size:0.74rem;">IO: {active['investigating_officer']}</div>
        <div style="color:#475569; font-size:0.72rem;">{active['police_station'][:38]}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Platform Operational Metrics ─────────────────────────────────
    dvi_stats = dvi_engine.get_statistics()
    ev_stats = evidence_engine.get_statistics()
    active_count = sum(1 for c in CASES if c["status"] == "Active")
    critical_count = sum(1 for c in CASES if c["priority"] == "Critical")

    st.markdown(f"""
    <div style="font-size:0.75rem; color:#94a3b8; line-height:1.9;">
        <div style="color:#ffffff; font-weight:800; margin-bottom:2px; letter-spacing:0.5px;">SYSTEM STATUS</div>
        <div>📁 Active Cases: <b style="color:#38bdf8;">{active_count}</b> &nbsp;|&nbsp; ⚠ <b style="color:#ef4444;">{critical_count} Crit</b></div>
        <div>🆔 Part 1 DVI: <b style="color:#a855f7;">{dvi_stats['high_confidence_candidates']} High Leads</b></div>
        <div>🔬 Part 2 FSL: <b style="color:#f59e0b;">{ev_stats['total_evidence']} Exhibits</b> (<b style="color:#ef4444;">{ev_stats['critical_priority']} Crit</b>)</div>
        <div>🗺️ Part 3 Hotspots: <b style="color:#06b6d4;">Ahmedabad Panel</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── BOB AGENT Sidebar Quick Trigger & Chat ───────────────────────
    with st.expander("🤖 Ask BOB AGENT (IBM)", expanded=False):
        sb_q = st.text_input("Ask a forensic question:", placeholder="e.g. How does DVI match?", key="sb_query_input", label_visibility="collapsed")
        if st.button("💬 Ask BOB", key="sb_submit_btn", type="primary", use_container_width=True) and sb_q:
            from core.bob_agent import bob_agent
            reply = bob_agent.query(sb_q)
            st.markdown(reply)

pages.run()
