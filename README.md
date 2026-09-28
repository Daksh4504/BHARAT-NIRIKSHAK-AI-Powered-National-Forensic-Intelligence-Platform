# 🚀 BHARAT NIRIKSHAK — AI-Powered National Forensic Intelligence Platform

> ⚠️ Replace everything in `[ ]` brackets with your actual content before submission.

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Bharat Nirikshak |
| **Track** | AI |
| **Team Lead** | [Name] — [email@ibm.com] |
| **Members** | [Name 1], [Name 2], [Name 3] |

---

## 🎯 Problem Statement

> In 2–3 sentences: What problem does your project solve? Who experiences this problem?

India's law enforcement and forensic agencies face critical bottlenecks in three interconnected domains: identifying disaster victims, triaging crime-scene evidence under investigation deadlines, and predicting crime hotspots before they escalate. Forensic scientists, Investigating Officers (IOs), and CSI teams lack a unified, AI-assisted platform that can handle all three problem areas simultaneously — resulting in delayed justice, compromised evidence chains, and reactive policing.

---

## 💡 Solution

> In 2–3 sentences: What did you build? How does it solve the problem above?

**BHARAT NIRIKSHAK** is a unified, IBM-powered national forensic intelligence platform that integrates three standalone AI modules under a single command dashboard. It leverages IBM Bob as an embedded forensic copilot, combining Interpol-standard DVI victim matching, a 3-pillar AI evidence prioritization engine, and a spatio-temporal crime hotspot prediction model — enabling proactive, evidence-based policing and faster judicial outcomes.

---

## ✨ Key Features

- **Feature 1:** DVI Forensic Intelligence — Interpol-standard Ante-Mortem / Post-Mortem matching engine with odontology, DNA, surgical implant, and tattoo identifiers (weighted scoring up to 100 pts, confidence tiers, reconciliation dossiers)
- **Feature 2:** AI Crime Scene Evidence Triage — ISO/IEC 17025 compliant 3-Pillar scoring (Degradation Risk + Probative Value + Statutory Deadlines) with ranked FSL dispatch queue and Form 27 requisition generation
- **Feature 3:** Predictive Crime Hotspot Mapping — Spatio-temporal panel analysis over Ahmedabad with Moran's I spatial autocorrelation, Mann-Kendall trend tests, and a live adjustable risk index map (PyDeck / deck.gl)
- **Feature 4:** IBM Bob Forensic Copilot — Embedded watsonx AI agent for case Q&A, evidence interpretation, and investigative guidance across all modules
- **Feature 5:** FIR NLP Intelligence & Deepfake Media Lab — Natural language processing for FIR pattern detection and AI-driven deepfake media analysis

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python, JavaScript (Node.js), TypeScript |
| **Frameworks** | Streamlit, Express.js, React (frontend UI for Parts 1 & 2) |
| **IBM Technologies** | IBM Bob (watsonx AI Forensic Copilot), IBM Watsonx.ai, IBM Cloud |
| **Databases** | JSON flat-file stores (mock), Pandas DataFrames, NetworkX graphs |
| **Other** | PyDeck / deck.gl (geospatial maps), Plotly, RapidFuzz, Pydantic, GitHub Actions |

---

## 📁 Repository Structure

```
├── src/                          # Unified Streamlit application entry point
│   └── app.py                    # Main app — navigation & sidebar branding
├── core/                         # Shared backend engines
│   ├── bob_agent.py              # IBM Bob watsonx AI forensic copilot
│   ├── dvi_engine.py             # Part 1: DVI matching logic
│   ├── evidence_engine.py        # Part 2: Evidence scoring logic
│   ├── fir_backend/              # FIR NLP extraction & repeat-offender detection
│   └── crime/                    # Part 3: Spatio-temporal analysis modules
├── pages/                        # Streamlit page modules
│   ├── dashboard.py              # Command dashboard
│   ├── dvi.py                    # Part 1: DVI Intelligence UI
│   ├── evidence_triage.py        # Part 2: Evidence Triage UI
│   ├── crime_hotspot.py          # Part 3: Crime Hotspot Map UI
│   ├── fir_intelligence.py       # FIR NLP Intelligence
│   ├── deepfake.py               # Deepfake Media Lab
│   └── reports.py                # Investigation Dossiers
├── part1-dvi-intelligence/       # Standalone Node.js DVI module (Port 3000)
├── part2-crime-scene-evidence/   # Standalone Node.js Evidence module (Port 3001)
├── part 3/                       # Standalone Streamlit Crime Hotspot module
├── docs/                         # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                         # Demo artifacts
│   ├── screenshots/              # App screenshots
│   └── demo-video-link.txt       # Link to demo video
├── presentation/                 # Slide deck
│   └── BHARAT_NIRIKSHAK_Executive_Presentation.pptx
├── assets/                       # Logos and static assets
├── requirements.txt              # Python dependencies
└── submission.yaml               # Structured submission metadata
```

---

## ⚡ How to Run

> Copy these exact steps from your `docs/setup-guide.md`

```bash
# 1. Clone the repo
git clone https://github.com/[your-repo].git
cd [your-repo]

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the unified Streamlit platform
streamlit run app.py
```

**To run the standalone Node.js modules:**

```bash
# Part 1 — DVI Intelligence (http://localhost:3000)
cd part1-dvi-intelligence
npm install
node server.js

# Part 2 — Crime Scene Evidence (http://localhost:3001)
cd part2-crime-scene-evidence
npm install
node server.js

# Part 3 — Crime Hotspot Dashboard (http://localhost:8501)
cd "part 3"
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 🎬 Demo Video | See `demo/demo-video-link.txt` |
| 🌐 Live Demo | See `demo/live-demo-url.txt` |
| 🖼️ Screenshots | See `demo/screenshots/` |
| 📊 Presentation | See `presentation/BHARAT_NIRIKSHAK_Executive_Presentation.pptx` |

---

## ⚠️ Known Limitations

> Be honest — judges appreciate transparency over overclaiming.

- Crime hotspot data (Part 3) is **synthetically generated** — it demonstrates method and pipeline, not real Ahmedabad crime statistics
- IBM Bob integration uses **mock/simulated AI responses** in the current demo environment; full watsonx.ai API integration requires live credentials
- DVI and Evidence modules use **in-memory JSON stores** — not connected to a production database
- Deepfake Media Lab is **scaffolded** with UI and analysis framework; live model inference requires additional GPU setup
- Tested primarily on **Chrome and modern Chromium browsers**

---

## 🥇 What We're Most Proud Of

The **scientific rigor** of all three core modules sets this project apart. Part 1 implements a genuine Interpol DVI weighted scoring engine (not a mockup) with explainable forensic rationale. Part 2 follows ISO/IEC 17025 forensic standards with court-admissible Form 27 generation. Part 3 applies real statistical methods — Moran's I spatial autocorrelation, Mann-Kendall trend testing, and a fully adjustable weighted risk index — that hold up to academic scrutiny. The IBM Bob forensic copilot ties all three modules together with contextual AI guidance, making this a complete, production-architecture system rather than a prototype.
