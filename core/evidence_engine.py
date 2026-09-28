"""
AI Crime Scene Evidence Prioritization Engine — ISO/IEC 17025 Compliant
Part 2 Engine for Bharat Nirikshan (ICIIP)

Implements:
- 3-Pillar Scientific Prioritization:
    1. Degradation & Perishability Risk (0-35 pts)
    2. Probative & Case Linkage Value (0-40 pts)
    3. Statutory Remand & Investigative Urgency (0-25 pts)
- 8 Forensic Disciplines Catalog with specific FSL laboratory tests and turnaround schedules
- Critical Forensic Preservation Alerts (Cold Chain, Faraday RF Bag, Rigid Casing, Inert Nylon, etc.)
- Ranked FSL Examination Queue with automated test mapping
- Official FSL Form 27 Evidence Requisition Requisition Dossier generator with SHA-256 custody verification
"""

from __future__ import annotations
import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime

PART2_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "part2-crime-scene-evidence", "data")

FORENSIC_TEST_CATALOG = {
    'Biological / DNA': {
        'tests': [
            'Presumptive Kastle-Meyer & Confirmatory RSID-Blood Assay',
            'Automated Chelex/Magnetic Bead DNA Extraction & Quantifiler Trio',
            '24-Plex Autosomal STR Profiling + Y-STR Male Lineage Sequencing',
            'Differential Lysis for Mixed Epithelial / Touch DNA Separation'
        ],
        'turnaroundUrgent': '12–24 Hours',
        'turnaroundRoutine': '5–7 Days',
        'specialPreservationAlert': '⚠️ CRITICAL BIO-HAZARD: Maintain strict cold chain (-20°C / 4°C). Store in breathable paper packaging to prevent mold/hydrolysis.'
    },
    'Digital / Cyber': {
        'tests': [
            'Volatile RAM Capture & Live State Memory Preservation',
            'Write-Blocked Physical Bit-Stream Image Acquisition (EnCase / FTK)',
            'Hardware Chip-Off / ISP JTAG Physical Extraction & Decryption',
            'Cellebrite UFED Advanced Logical & File System Extraction',
            'Geofence, GPS Coordinates & Encrypted Messaging Decryption'
        ],
        'turnaroundUrgent': '6–12 Hours (Battery / RAM volatile)',
        'turnaroundRoutine': '3–5 Days',
        'specialPreservationAlert': '⚠️ CRITICAL DIGITAL INTEGRITY: Keep isolated in Faraday RF Shielding bag. Connect external power pack to prevent power loss/kill switch activation.'
    },
    'Ballistics': {
        'tests': [
            'Comparison Microscopy (Stereo 40x) for Striation & Toolmark Concordance',
            'Firing Pin Indentation, Breech Face & Ejector Mark 3D Topography',
            'IBIS (Integrated Ballistics Identification System) TraxHD Database Ingestion',
            'SEM-EDX (Scanning Electron Microscopy) for Gunshot Residue (GSR) Primer Analysis'
        ],
        'turnaroundUrgent': '24–48 Hours',
        'turnaroundRoutine': '7–10 Days',
        'specialPreservationAlert': '⚠️ BALLISTIC INTEGRITY: Protect firing pin indent and extractor rim from metallic contact. Package in rigid padded container.'
    },
    'Latent Fingerprints': {
        'tests': [
            'Cyanoacrylate Ester (Superglue) Vacuum Chamber Fuming',
            'Fluorescent Dye Staining (Rhodamine 6G / RAM) & Forensic Light Source (450nm)',
            'Automated Fingerprint Identification System (AFIS) 12-Minutiae Search',
            'Ninhydrin / DFO Chemical Fuming for Porous Substrates'
        ],
        'turnaroundUrgent': '12–24 Hours',
        'turnaroundRoutine': '3–4 Days',
        'specialPreservationAlert': '⚠️ FRICTION RIDGE PRESERVATION: Avoid friction contact with surface. Protect from humidity degradation and direct sunlight.'
    },
    'Chemical / Explosives': {
        'tests': [
            'Gas Chromatography-Mass Spectrometry (GC-MS) for High Explosive Residues',
            'High-Performance Liquid Chromatography (HPLC) for PETN/RDX Nitroaromatics',
            'FTIR (Fourier Transform Infrared Spectroscopy) for Oxidizer Identification',
            'Ion Chromatography (IC) for Inorganic Explosive Precursors'
        ],
        'turnaroundUrgent': '12–18 Hours',
        'turnaroundRoutine': '3–5 Days',
        'specialPreservationAlert': '⚠️ HAZMAT / VOLATILE RESIDUE: Package in airtight inert nylon / metal containers to prevent volatile vapor evaporation.'
    },
    'Trace / Fiber': {
        'tests': [
            'Polarized Light Microscopy (PLM) & Refractive Index Measurement',
            'Micro-FTIR Spectrometry for Polymer Classification',
            'Microspectrophotometry (MSP) for Dye Chromatographic Comparison',
            'Cross-Sectional Morphology & Scanning Electron Microscopy'
        ],
        'turnaroundUrgent': '48 Hours',
        'turnaroundRoutine': '5–8 Days',
        'specialPreservationAlert': '⚠️ TRACE INTEGRITY: Seal in glassine envelopes to prevent static loss or ambient dust contamination.'
    },
    'Questioned Documents': {
        'tests': [
            'Video Spectral Comparator (VSC 8000) for Infrared Luminescence / Char Reconstruction',
            'Electrostatic Detection Apparatus (ESDA) for Indented Handwriting Impressions',
            'High-Performance Thin Layer Chromatography (HPTLC) for Ink Composition',
            'Microscopic Line Cross & Sequence of Strokes Analysis'
        ],
        'turnaroundUrgent': '24–48 Hours',
        'turnaroundRoutine': '5–7 Days',
        'specialPreservationAlert': '⚠️ FRAGILE DOCUMENT: Do not unfold or press charred remnants. Support in polyester batting boxes.'
    },
    'Physical / Toolmark': {
        'tests': [
            'Comparative Toolmark Microscopy with Test Casts in Soft Lead / Clay',
            'Mikrosil Silicone Casting of Negative Tool Impressions',
            'Hardness & Metallurgical Trace Composition Analysis'
        ],
        'turnaroundUrgent': '48 Hours',
        'turnaroundRoutine': '7 Days',
        'specialPreservationAlert': '⚠️ TOOLMARK CARE: Never insert suspect tool into questioned impression mark directly.'
    }
}


class EvidenceEngine:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or PART2_DATA_DIR
        self._cases: List[Dict[str, Any]] = []
        self._evidence: List[Dict[str, Any]] = []
        self._fsl_reports: List[Dict[str, Any]] = []
        self.load_data()

    def load_data(self) -> None:
        """Load JSON datasets from Part 2 data folder."""
        cases_file = os.path.join(self.data_dir, "cases.json")
        if os.path.exists(cases_file):
            with open(cases_file, "r", encoding="utf-8") as f:
                self._cases = json.load(f)
        else:
            self._cases = []

        ev_file = os.path.join(self.data_dir, "evidence.json")
        if os.path.exists(ev_file):
            with open(ev_file, "r", encoding="utf-8") as f:
                self._evidence = json.load(f)
        else:
            self._evidence = []

        rep_file = os.path.join(self.data_dir, "fsl_reports.json")
        if os.path.exists(rep_file) and os.path.getsize(rep_file) > 5:
            try:
                with open(rep_file, "r", encoding="utf-8") as f:
                    self._fsl_reports = json.load(f)
            except Exception:
                self._fsl_reports = []
        else:
            self._fsl_reports = []

    def get_cases(self) -> List[Dict[str, Any]]:
        return list(self._cases)

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        for c in self._cases:
            if c.get("id") == case_id or c.get("case_id") == case_id:
                return c
        return None

    def get_all_evidence(self, case_id: Optional[str] = None, evidence_type: Optional[str] = None) -> List[Dict[str, Any]]:
        res = []
        for e in self._evidence:
            if case_id and e.get("caseId") != case_id and e.get("case_id") != case_id:
                continue
            if evidence_type and evidence_type != "All":
                t = e.get("evidenceType") or e.get("evidence_type") or ""
                if evidence_type.lower() not in t.lower():
                    continue
            res.append(e)
        return res

    def get_evidence_by_id(self, ev_id: str) -> Optional[Dict[str, Any]]:
        for e in self._evidence:
            if e.get("id") == ev_id or e.get("evidence_id") == ev_id:
                return e
        return None

    def calculate_priority(self, evidence: Dict[str, Any], crime_case: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """ISO/IEC 17025 3-Pillar Forensic Evidence Prioritization Calculator."""
        ev_type = evidence.get("evidenceType") or evidence.get("evidence_type") or "Physical / Toolmark"
        deg_in = str(evidence.get("degradationRisk", "MEDIUM")).upper()
        prob_in = str(evidence.get("probativeValue", "HIGH")).upper()
        urg_in = str(evidence.get("statutoryUrgency", "MEDIUM")).upper()

        # Pillar 1: Degradation & Perishability (0 - 35 pts)
        if deg_in == 'CRITICAL':
            deg_score = 35
            deg_note = 'Extreme risk of rapid biological degradation / volatile power/RAM loss.'
        elif deg_in == 'HIGH':
            deg_score = 28
            deg_note = 'High perishability (active bacterial decomposition / volatile solvent evaporation).'
        elif deg_in == 'MEDIUM':
            deg_score = 18
            deg_note = 'Moderate shelf stability under standard controlled forensic packaging.'
        else:
            deg_score = 8
            deg_note = 'High physical stability; negligible degradation risk under ambient storage.'

        # Pillar 2: Probative & Case Linkage (0 - 40 pts)
        if prob_in == 'CRITICAL':
            prob_score = 40
            prob_note = 'Direct physical nexus to core crime act, prime suspect, or primary murder weapon.'
        elif prob_in == 'HIGH':
            prob_score = 32
            prob_note = 'Strong corroborative linkage connecting suspect identity, MO, or crime scene presence.'
        elif prob_in == 'MEDIUM':
            prob_score = 20
            prob_note = 'Secondary contextual evidence corroborating sequence of events or timeline.'
        else:
            prob_score = 10
            prob_note = 'Circumstantial or ambient background trace; non-individualizing value.'

        # Pillar 3: Statutory & Remand Urgency (0 - 25 pts)
        if urg_in == 'CRITICAL':
            urg_score = 25
            urg_note = 'Active fleeing suspect / mandatory 24-hour statutory judicial remand filing deadline.'
        elif urg_in == 'HIGH':
            urg_score = 18
            urg_note = 'Priority charge-sheet timeline / crucial lead for ongoing suspect interrogation.'
        elif urg_in == 'MEDIUM':
            urg_score = 12
            urg_note = 'Standard judicial investigation queue; trial preparation schedule.'
        else:
            urg_score = 5
            urg_note = 'Routine investigative archive; non-urgent judicial timeline.'

        total_score = min(100, max(10, deg_score + prob_score + urg_score))

        # Tiers
        if total_score >= 85:
            tier = 'CRITICAL'
            badge_color = 'danger'
            hex_color = '#ef4444'
            queue_action = '🚨 IMMEDIATE LAB DISPATCH (Within 6–12 Hours)'
        elif total_score >= 70:
            tier = 'HIGH'
            badge_color = 'warning'
            hex_color = '#f97316'
            queue_action = '⚡ Priority Lab Queue (Dispatch within 24 Hours)'
        elif total_score >= 50:
            tier = 'MEDIUM'
            badge_color = 'info'
            hex_color = '#eab308'
            queue_action = '📦 Standard FSL Queue (Dispatch within 3–5 Days)'
        else:
            tier = 'LOW'
            badge_color = 'secondary'
            hex_color = '#22c55e'
            queue_action = '📁 Secondary Corroborative Archive'

        # Fetch Test Mapping
        norm_type = ev_type
        # normalize fuzzy names
        for cat in FORENSIC_TEST_CATALOG:
            if cat.lower() in ev_type.lower() or ev_type.lower() in cat.lower():
                norm_type = cat
                break
        test_info = FORENSIC_TEST_CATALOG.get(norm_type, FORENSIC_TEST_CATALOG['Physical / Toolmark'])

        reason = (
            f"Priority classified as {tier} ({total_score}/100) based on ISO/IEC 17025 triage: "
            f"{prob_note} {deg_note} {urg_note}"
        )

        return {
            "priorityLevel": tier,
            "priorityScore": total_score,
            "badgeColor": badge_color,
            "hexColor": hex_color,
            "queueAction": queue_action,
            "scoreBreakdown": {
                "degradationScore": deg_score,
                "degradationMax": 35,
                "degradationNote": deg_note,
                "probativeScore": prob_score,
                "probativeMax": 40,
                "probativeNote": prob_note,
                "urgencyScore": urg_score,
                "urgencyMax": 25,
                "urgencyNote": urg_note
            },
            "reason": reason,
            "recommendedTests": test_info['tests'],
            "estimatedTurnaround": test_info['turnaroundUrgent'] if tier == 'CRITICAL' else test_info['turnaroundRoutine'],
            "preservationAlert": test_info['specialPreservationAlert'],
            "requiresUrgentLabDispatch": tier == 'CRITICAL' or deg_in == 'CRITICAL'
        }

    def build_fsl_queue(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Ranked FSL examination queue sorted by ISO/IEC 17025 composite score."""
        ev_list = self.get_all_evidence(case_id=case_id)
        queue = []
        for e in ev_list:
            analysis = self.calculate_priority(e)
            queue.append({**e, **analysis})

        queue.sort(key=lambda x: x["priorityScore"], reverse=True)
        return queue

    def add_evidence_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Log new crime scene evidence and auto-calculate priority."""
        if not item.get("id"):
            cid = item.get("caseId", "CASE").replace("CASE-", "")
            item["id"] = f"EV-{cid}-{len(self._evidence)+1:02d}"
        if not item.get("collectionTimestamp"):
            item["collectionTimestamp"] = datetime.now().isoformat()
        if not item.get("custodyStatus"):
            item["custodyStatus"] = "Sealed in Evidence Locker"
        if not item.get("fslQueueStatus"):
            item["fslQueueStatus"] = "Queued for Examination"

        self._evidence.append(item)
        return item

    def generate_form_27(
        self,
        case_id: str,
        evidence_ids: List[str],
        courier_officer: str,
        destination_fsl: str,
        court_case_ref: str,
        dispatching_io: str
    ) -> Dict[str, Any]:
        """Generate official FSL Form 27 Requisition Manifest with SHA-256 tamper-evident hash."""
        selected = [e for e in self._evidence if (e.get("id") in evidence_ids or e.get("evidence_id") in evidence_ids)]
        enriched_items = []
        for item in selected:
            analysis = self.calculate_priority(item)
            enriched_items.append({
                "id": item.get("id") or item.get("evidence_id"),
                "name": item.get("evidenceName") or item.get("description", "Unnamed Item"),
                "type": item.get("evidenceType") or item.get("evidence_type"),
                "priorityScore": analysis["priorityScore"],
                "priorityLevel": analysis["priorityLevel"],
                "preservationAlert": analysis["preservationAlert"],
                "recommendedTests": analysis["recommendedTests"],
                "packaging": item.get("packagingDetails", "Standard Tamper-Evident Bag")
            })

        manifest_id = f"FSL-REQ-{datetime.now().strftime('%Y%m%d')}-{len(self._fsl_reports)+1:03d}"
        payload_for_hash = f"{manifest_id}|{case_id}|{','.join(evidence_ids)}|{datetime.now().isoformat()}"
        custody_hash = hashlib.sha256(payload_for_hash.encode()).hexdigest().upper()

        dossier = {
            "manifestId": manifest_id,
            "caseId": case_id,
            "courtCaseRef": court_case_ref or "Spl. Sessions Court No. 4 / Remand Order",
            "destinationFsl": destination_fsl or "Central Forensic Science Laboratory (CFSL / State FSL)",
            "courierOfficer": courier_officer or "CSI Special Courier Officer",
            "dispatchingIo": dispatching_io or "Lead Investigating Officer",
            "dispatchTimestamp": datetime.now().isoformat(),
            "itemsCount": len(enriched_items),
            "evidenceItems": enriched_items,
            "tamperEvidentHash": custody_hash,
            "chainOfCustodyPledge": (
                "Certified that the seized exhibits listed herein have been sealed in tamper-evident packaging "
                "with unbroken wax seals and official brass seals under Section 293 CrPC (Section 329 BNSS 2023). "
                "Strict temperature and physical integrity protocols have been observed during transit."
            )
        }

        self._fsl_reports.append(dossier)
        return dossier

    def get_fsl_reports(self) -> List[Dict[str, Any]]:
        return list(self._fsl_reports)

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self._evidence)
        queue = self.build_fsl_queue()
        critical = sum(1 for e in queue if e.get("priorityLevel") == "CRITICAL")
        high = sum(1 for e in queue if e.get("priorityLevel") == "HIGH")
        urgent_alerts = sum(1 for e in queue if e.get("requiresUrgentLabDispatch"))

        return {
            "total_evidence": total,
            "critical_priority": critical,
            "high_priority": high,
            "urgent_lab_dispatch_required": urgent_alerts,
            "fsl_reports_generated": len(self._fsl_reports),
            "total_cases_tracked": len(self._cases)
        }


# Singleton engine instance
evidence_engine = EvidenceEngine()
