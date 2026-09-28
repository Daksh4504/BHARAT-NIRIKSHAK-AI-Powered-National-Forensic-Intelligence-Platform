# 🚔 Part 1: DVI Intelligence Module
*Forensic Disaster Victim Identification System (Based on Problem #02)*

A standalone, functional forensic intelligence application built according to **Interpol Disaster Victim Identification (DVI)** standards for matching Ante-Mortem (AM) missing persons records against Post-Mortem (PM) unidentified remains.

---

## 🌟 Features Implemented

1. **Structured Ante-Mortem (AM) Records**:
   - Demographic profile (Name, Case Ref, Age, Gender, Height, Build, Blood Group)
   - Physical descriptors (Hair, Eyes, Complexion)
   - Distinctive marks (Surgical scars, trauma marks, tattoos)
   - Odontology / Dental Charting (Crowns, missing teeth, restorations, braces)
   - Surgical and orthopedic implants history
   - Clothing and personal property / jewelry items
   - DNA reference sample status and next-of-kin reporting info

2. **Structured Post-Mortem (PM) Records**:
   - Recovery location / grid sector, recovery number, and date
   - Biological sex, estimated age range, and cadaveric stature with tolerance
   - Remains condition and thermal/trauma disruption level
   - Post-mortem dental findings (restorative markers, tooth charting)
   - Observed surgical hardware, scars, and tattoos
   - Textile fragments and personal effects recovered on remains
   - DNA STR processing status and fingerprint availability

3. **Transparent Scientific Matching Engine**:
   - **Primary Identifiers (Highest Weight)**: Odontology / Dental Concordance (up to 30 pts), DNA STR Profile (up to 25 pts), Dactyloscopy.
   - **Secondary Identifiers**: Surgical scars, orthopedic hardware (e.g. titanium plates), anatomical anomalies, tattoos (up to 35 pts).
   - **Auxiliary Identifiers**: Matching apparel textiles and monogrammed/personalized jewelry (up to 20 pts).
   - **Exclusionary Logic**: Automatic penalties and flags for hard biological sex or severe anthropometric disparities.

4. **Top 3 Candidate Matches Display**:
   - Concordance score percentage (0–100%) and confidence tier classification.
   - Side-by-side comparative inspection matrix with color-coded status badges:
     - 🟢 **Conclusive Match**
     - 🟡 **Compatible**
     - 🔴 **Conflict / Mismatch**
     - ⚪ **Inconclusive**
   - **Forensic Rationale Summary**: Explainable narrative outlining why each candidate matched, highlighting primary identifiers first.

5. **Case Triage Dashboard**:
   - Operational metrics ticker (Total PM, Total AM, High-Confidence matches, Reconciled dossiers, Backlog).
   - Real-time unidentified remains triage board with live auto-match scores.

6. **Interpol-Format Reconciliation Reports**:
   - Full DVI Reconciliation Dossier with victim details, recovery site, scientific concordance index, and forensic rationale.
   - Formal sign-off blocks for Lead Forensic Pathologist, Chief Odontologist, and Investigating Officer.
   - Print & PDF export ready formatting (`@media print`).

---

## 🚀 How to Run

### Option 1: From the project root (`c:\Users\ratho\Desktop\IBM`)
```bash
npm start
```

### Option 2: Directly inside `part1-dvi-intelligence`
```bash
cd part1-dvi-intelligence
node server.js
```

Open your browser at:
👉 **`http://localhost:3000`**

---

## 📁 Module File Structure

```
part1-dvi-intelligence/
├── data/
│   ├── disaster_case.json     # Active disaster incident metadata
│   ├── antemortem.json        # 5 realistic missing persons profiles
│   ├── postmortem.json        # 4 unidentified human remains profiles
│   └── reconciliations.json   # Verified reconciliation certificates
├── public/
│   ├── index.html             # Responsive forensic investigation interface
│   ├── styles.css             # Forensic tactical dark theme & print styles
│   └── app.js                 # State management, API calls, and UI logic
├── matching_engine.js         # Interpol DVI weighted scoring & rationale engine
├── package.json               # Module dependencies
├── README.md                  # Documentation
└── server.js                  # Express backend & REST API
```

---

## 🔌 REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/incident` | GET | Operational disaster metadata and triage statistics |
| `/api/antemortem` | GET / POST | List all or file a new Ante-Mortem missing person profile |
| `/api/postmortem` | GET / POST | List all or log a new Post-Mortem unidentified body |
| `/api/match/pm/:id` | POST | Evaluate Top 3 AM candidate matches for a PM body |
| `/api/match/batch` | GET | Evaluate global batch matrix across all PMs and AMs |
| `/api/reconcile` | POST | Formally certify reconciliation with pathologist sign-off |
| `/api/reconciliations` | GET | List all certified DVI reconciliation dossiers |
| `/api/reports/reconciliation/:id` | GET | Retrieve complete printable DVI dossier |
