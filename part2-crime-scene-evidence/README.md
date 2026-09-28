# 🔍 Part 2: AI Crime Scene Evidence Prioritization
*Forensic Evidence Triage & FSL Dispatch Queue (Based on Problem #03)*

A standalone, functional forensic intelligence application designed for Crime Scene Investigators (CSI) and Investigating Officers (IO) to log, evaluate, prioritize, and schedule crime-scene physical and digital evidence for Forensic Science Laboratory (FSL) examination.

---

## 🌟 Features Implemented

1. **Crime Scene Case Management**:
   - Create and switch between active crime scenes (Homicide, Armed Robbery, Kidnapping, Cyber Forensics).
   - Track case metadata (Case ID, Crime classification IPC/BNS, Scene location, Incident date, IO & CSI Leads).

2. **Multi-Category Evidence Logging**:
   - Support for 8 specialized forensic categories:
     - 🧬 **Biological / DNA** (Blood, touch epithelial, saliva, hair roots)
     - 💻 **Digital / Cyber** (Smartphones, encrypted storage, keystroke injectors, RAM)
     - 💥 **Ballistics** (Spent casings, deformed projectiles, GSR swabs, firearms)
     - 🖐️ **Latent Fingerprints** (Friction ridge impressions, acetate lifts)
     - 🧪 **Chemical / Explosives** (Detonator cords, accelerants, toxic substances)
     - 🧶 **Trace / Fiber** (Textile transfers, paint chips, glass shards)
     - 📄 **Questioned Documents** (Charred paper, indented handwriting, forged deeds)
     - 🔧 **Physical / Toolmark** (Pry bars, tool impressions, silicone casts)

3. **Transparent 3-Pillar Priority Scoring Engine (`prioritization_engine.js`)**:
   - **Degradation & Perishability Risk (0–35 pts)**: Biological decay, volatile digital memory loss, evaporating chemical residues.
   - **Probative & Case Linkage Value (0–40 pts)**: Direct nexus to murder weapon or prime suspect vs circumstantial context.
   - **Statutory Remand & Investigation Deadlines (0–25 pts)**: Fleeing suspects, 24-hour judicial remand deadlines, charge-sheet schedules.
   - **Composite Score (0–100 pts)** mapped to **CRITICAL**, **HIGH**, **MEDIUM**, and **LOW** tiers.

4. **Ranked FSL Examination Queue**:
   - Prioritized order for forensic laboratory ingestion.
   - Auto-mapped recommended forensic tests (e.g., 24-plex STR DNA profiling, Cellebrite UFED chip-off, SEM-EDX GSR analysis, AFIS 12-minutiae matching).
   - Estimated turnaround times (e.g. 6–12h for volatile digital/perishable biological vs 5–7 days for routine trace).
   - **Special Preservation Alerts** (Cold chain -20°C, Faraday RF shielding bags, anti-static inert seals).

5. **Live Triage & Dynamic Filtering**:
   - Filter by Priority (*Critical, High, Medium, Low*).
   - Filter by Evidence Type (*Biological, Digital, Ballistics, etc.*).
   - Real-time search by location, item name, and description.
   - Real-time priority preview inside the "Log Evidence" modal as parameters are adjusted.

6. **Official FSL Form 27 Requisition Reports**:
   - Generates standardized court-admissible Form 27 / Evidence Requisition Manifest.
   - Includes tamper-evident chain of custody hashes, courier details, and signature blocks.
   - Print & PDF export ready (`@media print`).

---

## 🚀 How to Run

### Option 1: From the project root
```bash
npm run part2
```

### Option 2: Directly inside `part2-crime-scene-evidence`
```bash
cd part2-crime-scene-evidence
node server.js
```

Open your browser at:
👉 **`http://localhost:3001`**

---

## 📁 Module File Structure

```
part2-crime-scene-evidence/
├── data/
│   ├── cases.json              # Active crime scene cases
│   ├── evidence.json           # Preloaded multi-type evidence items
│   └── fsl_reports.json        # Issued Form 27 requisition dossiers
├── public/
│   ├── index.html              # Responsive tactical forensic UI
│   ├── styles.css              # Dark tactical styling & print stylesheet
│   └── app.js                  # Frontend state, filters, and modals
├── prioritization_engine.js    # ISO/IEC 17025 multi-factor scoring engine
├── package.json                # Module dependencies
├── README.md                   # Documentation
└── server.js                   # Express backend (Port 3001)
```

---

## 🔌 REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/cases` | GET / POST | List all cases or create a new crime scene case |
| `/api/cases/:id` | GET | Retrieve case info with enriched evidence and metrics |
| `/api/evidence` | GET / POST | List filtered evidence or log a new evidence item |
| `/api/analyze-preview` | POST | Live priority calculation preview for form inputs |
| `/api/queue/:caseId` | GET | Ranked FSL examination queue with test mappings |
| `/api/fsl-report` | POST | Issue official Form 27 FSL requisition report |
| `/api/fsl-reports` | GET | List all generated FSL submission dossiers |
| `/api/fsl-reports/:id` | GET | Retrieve a specific Form 27 dossier for print |
