"""
Central Case Database — the integration backbone of the ICIIP platform.

Every module attaches its data to a CaseRecord via case_id.
Mock data is seeded here so the entire platform works without external APIs.
"""

from __future__ import annotations
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

# ─────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────

@dataclass
class EvidenceItem:
    evidence_id: str
    case_id: str
    description: str
    evidence_type: str          # Physical, Digital, Biological, Documentary
    priority: str               # Critical, High, Medium, Low
    chain_of_custody: str
    location_found: str
    collected_by: str
    date_collected: str
    lab_status: str             # Pending, Processing, Completed
    lab_result: str
    notes: str = ""


@dataclass
class DVIRecord:
    dvi_id: str
    case_id: str
    victim_name: str
    status: str                 # Identified, Unidentified, Partial
    method_used: str            # Fingerprint, DNA, Dental, Visual, Document
    confidence: float           # 0.0 – 100.0
    ante_mortem_ref: str
    post_mortem_ref: str
    identification_date: str
    examiner: str
    notes: str = ""


@dataclass
class DeepfakeResult:
    analysis_id: str
    case_id: str
    media_type: str             # Video, Image, Audio
    file_description: str
    is_manipulated: bool
    confidence_score: float     # 0–100
    detection_model: str
    manipulation_type: str
    frame_analysis: str
    metadata_flags: List[str] = field(default_factory=list)
    submitted_at: str = ""


@dataclass
class HotspotPin:
    pin_id: str
    case_id: str
    latitude: float
    longitude: float
    zone_label: str
    crime_type: str
    severity: str
    timestamp: str
    note: str = ""


@dataclass
class CaseRecord:
    case_id: str
    title: str
    status: str                 # Active, Closed, Suspended, Referred
    priority: str               # Critical, High, Medium, Low
    crime_type: str
    date_opened: str
    investigating_officer: str
    police_station: str
    district: str
    victim_names: List[str] = field(default_factory=list)
    accused_names: List[str] = field(default_factory=list)
    fir_text: str = ""
    fir_extracted: Optional[Dict[str, Any]] = None
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    dvi_records: List[DVIRecord] = field(default_factory=list)
    deepfake_results: List[DeepfakeResult] = field(default_factory=list)
    hotspot_pins: List[HotspotPin] = field(default_factory=list)
    similar_cases: List[str] = field(default_factory=list)
    investigation_findings: str = ""
    last_updated: str = ""
    location: str = ""


# ─────────────────────────────────────────────────────────────────────
# MOCK SEED DATA
# ─────────────────────────────────────────────────────────────────────

def _make_evidence(case_id: str, items: List[Dict]) -> List[EvidenceItem]:
    return [EvidenceItem(evidence_id=f"EV-{case_id}-{i+1:03d}", case_id=case_id, **item)
            for i, item in enumerate(items)]


def _make_dvi(case_id: str, records: List[Dict]) -> List[DVIRecord]:
    return [DVIRecord(dvi_id=f"DVI-{case_id}-{i+1:03d}", case_id=case_id, **r)
            for i, r in enumerate(records)]


MOCK_CASES: List[CaseRecord] = [

    CaseRecord(
        case_id="CASE-2024-001",
        title="Old Airport Road Chain Snatching Series",
        status="Active",
        priority="Critical",
        crime_type="Snatching / Robbery",
        date_opened="2024-07-15",
        investigating_officer="SI Ramesh Kumar",
        police_station="HAL Police Station, Bengaluru",
        district="Bengaluru East",
        victim_names=["Meenakshi Sundaram", "Kavita Rao", "Sunita Rao"],
        accused_names=["Bunty @ Rakesh", "Kallu @ Vikram"],
        location="Old Airport Road / Koramangala corridor, Bengaluru",
        fir_text="""FIRST INFORMATION REPORT
Police Station: HAL Police Station, Bengaluru City
Date & Time of Report: 15/07/2024 at 21:10 Hrs
Date & Time of Occurrence: 15/07/2024 at 20:00 Hrs
Place of Occurrence: Near Manipal Hospital Bus Stop, Old Airport Road, Bengaluru

Complainant / Victim: Mrs. Meenakshi Sundaram, Aged 46 years

Statement: Today evening at around 8:00 PM, I was walking along Old Airport Road. Two unknown men on a high-speed black Bajaj Pulsar motorcycle with registration KA-03-HX-4812 approached me from behind. The pillion rider forcefully snatched my 24-carat gold chain weighing 32 grams (Rs. 2,10,000) from my neck. They sped away towards Marathahalli flyover.

Sections: IPC 392 (Robbery), IPC 34""",
        similar_cases=["FIR-2024-0812", "FIR-2024-0945", "FIR-2024-1750"],
        investigation_findings="Suspect vehicle KA-03-HX-4812 traced to Bunty @ Rakesh. Three linked incidents across East and South Zone. ANPR alerts active across 12 junctions.",
        last_updated="2024-07-22",
        evidence_items=_make_evidence("CASE-2024-001", [
            {"description": "CCTV footage from Manipal Hospital junction", "evidence_type": "Digital",
             "priority": "Critical", "chain_of_custody": "SI Kumar → SOCO Lab",
             "location_found": "Old Airport Road Camera #7", "collected_by": "SI Ramesh Kumar",
             "date_collected": "2024-07-15", "lab_status": "Completed",
             "lab_result": "Clear image of KA-03-HX-4812 confirmed. Face partially visible."},
            {"description": "Gold chain recovered fragment (8g)", "evidence_type": "Physical",
             "priority": "High", "chain_of_custody": "Beat constable → Property Room",
             "location_found": "Near bus stop footpath", "collected_by": "PC Venkat",
             "date_collected": "2024-07-15", "lab_status": "Completed",
             "lab_result": "Gold purity: 22K. Matches victim's jeweller records."},
            {"description": "Witness statement — auto driver Raju M", "evidence_type": "Documentary",
             "priority": "High", "chain_of_custody": "SI Kumar → Case File",
             "location_found": "Old Airport Road", "collected_by": "SI Ramesh Kumar",
             "date_collected": "2024-07-16", "lab_status": "Completed",
             "lab_result": "Corroborates vehicle registration and suspect description."},
            {"description": "Fingerprint swab from lamppost touched by pillion", "evidence_type": "Biological",
             "priority": "Medium", "chain_of_custody": "SOCO → FSL Bengaluru",
             "location_found": "Lamppost near snatching site", "collected_by": "SOCO Officer Priya",
             "date_collected": "2024-07-16", "lab_status": "Processing",
             "lab_result": "Awaiting AFIS match result."},
        ]),
        hotspot_pins=[
            HotspotPin("HP-001-A", "CASE-2024-001", 12.9716, 77.5946, "East Zone", "Snatching / Robbery", "High", "2024-07-15 20:00"),
            HotspotPin("HP-001-B", "CASE-2024-001", 12.9279, 77.6271, "South-East Zone", "Snatching / Robbery", "High", "2024-03-28 20:15"),
            HotspotPin("HP-001-C", "CASE-2024-001", 12.9254, 77.5840, "South Zone", "Snatching / Robbery", "Medium", "2024-06-10 20:30"),
        ]
    ),

    CaseRecord(
        case_id="CASE-2024-002",
        title="BESCOM APK Phishing Fraud Ring — Jayanagar & Indiranagar",
        status="Active",
        priority="High",
        crime_type="Cyber Fraud / Financial Scam",
        date_opened="2024-07-20",
        investigating_officer="SI Pooja Iyer",
        police_station="Cyber Crime PS, Bengaluru CID",
        district="Bengaluru Central",
        victim_names=["Dr. Harish Chandra", "Venkatesh Murthy", "Anand Kulkarni"],
        accused_names=["Manoj Kumar @ Rajat", "Ramesh Shah (Mule Account)"],
        location="Online / Cyber — Victims across Indiranagar, Jayanagar, Malleshwaram",
        fir_text="""FIRST INFORMATION REPORT
Police Station: Cyber Crime Police Station, Central Division
Complainant: Dr. Harish Chandra, Age 67 Years, Retired Professor.

On 20th July 2024 at 10:45 AM, I received a fake SMS claiming electricity bill disconnection. On calling +91-9876543210, a caller named 'Officer Rajat Kumar from BESCOM' instructed me to install BESCOM_QuickPay_Update.apk via WhatsApp. Upon installation, Rs 5,20,000 was debited in three RTGS transactions to beneficiary Ramesh Shah.

Sections: IT Act 66D, IPC 420, IPC 120B""",
        similar_cases=["FIR-2024-1102", "FIR-2024-1240"],
        investigation_findings="Number +91-9876543210 traced to Jamtara, Jharkhand. CDR shows 47 calls to Bengaluru victims in 30 days. Mule account frozen. Rs 1.2 Lakh recovered so far.",
        last_updated="2024-07-28",
        evidence_items=_make_evidence("CASE-2024-002", [
            {"description": "Malicious APK file BESCOM_QuickPay_Update.apk", "evidence_type": "Digital",
             "priority": "Critical", "chain_of_custody": "Victim → Cyber Cell",
             "location_found": "Victim's mobile phone (HDFC App data)", "collected_by": "SI Pooja Iyer",
             "date_collected": "2024-07-20", "lab_status": "Completed",
             "lab_result": "Contains AnyDesk-based screen-mirroring payload. Malware classification: RAT/FraudBridge."},
            {"description": "Call Detail Records for +91-9876543210", "evidence_type": "Digital",
             "priority": "Critical", "chain_of_custody": "Telecom operator → Cyber Cell",
             "location_found": "Telecom server (TRAI requisition)", "collected_by": "Inspector Mehta",
             "date_collected": "2024-07-23", "lab_status": "Completed",
             "lab_result": "47 victim calls detected. Tower location: Jamtara, Jharkhand."},
            {"description": "Bank account statements — Ramesh Shah mule account", "evidence_type": "Documentary",
             "priority": "High", "chain_of_custody": "SBI Legal → Cyber Cell",
             "location_found": "SBI Branch Jamtara (freeze order)", "collected_by": "Inspector Mehta",
             "date_collected": "2024-07-24", "lab_status": "Completed",
             "lab_result": "Rs 3.2 Lakh frozen. Onward transfer to 4 crypto wallets detected."},
        ]),
        hotspot_pins=[
            HotspotPin("HP-002-A", "CASE-2024-002", 12.9667, 77.6430, "Cyber Crime Jurisdiction", "Cyber Fraud", "High", "2024-07-20 11:00"),
        ]
    ),

    CaseRecord(
        case_id="CASE-2024-003",
        title="Rainbow Layout Villa Burglary — Sarjapur Road",
        status="Active",
        priority="High",
        crime_type="House Burglary / Breaking by Night",
        date_opened="2024-08-04",
        investigating_officer="ASI Nagaraj B",
        police_station="Bellandur Police Station",
        district="Bengaluru South-East",
        victim_names=["Vikramaditya Sen"],
        accused_names=["Iron Rod Syndicate (3 unidentified masked men)"],
        location="Rainbow Residential Layout, Sarjapur Main Road, Bengaluru",
        fir_text="""FIR — Bellandur Police Station
Complainant: Mr. Vikramaditya Sen, Age 52 Years

Our family returned from Ooty holiday to find the villa burglarized. Rear kitchen iron security grills were cut with a hydraulic bolt cutter. Bedroom lockers pried open. CCTV DVR stolen. Stolen: Gold jewelry (120g), Cash Rs 3 Lakh, 2 Swiss watches. CCTV at Sarjapur junction recorded a white Maruti Swift Dzire picking up 3 masked men at 03:42 AM.

Sections: IPC 457, IPC 380, IPC 34""",
        similar_cases=["FIR-2024-1315", "FIR-2024-1420"],
        investigation_findings="White Swift Dzire traced to fake registration. Crime series matches 6 similar villa burglaries in HSR, Bellandur, Whitefield over 90 days. Syndicate believed to be 4-5 members operating from Tumkur.",
        last_updated="2024-08-10",
        evidence_items=_make_evidence("CASE-2024-003", [
            {"description": "Hydraulic bolt cutter blade fragment", "evidence_type": "Physical",
             "priority": "Critical", "chain_of_custody": "ASI Nagaraj → FSL",
             "location_found": "Rear kitchen window sill", "collected_by": "SOCO Team",
             "date_collected": "2024-08-04", "lab_status": "Completed",
             "lab_result": "Industrial grade. Tool marks match marks from FIR-2024-1315 (HSR Layout)."},
            {"description": "Footprint casts (3 suspects, rear boundary wall)", "evidence_type": "Physical",
             "priority": "High", "chain_of_custody": "SOCO → FSL",
             "location_found": "Rear boundary wall top / ground", "collected_by": "SOCO Officer Priya",
             "date_collected": "2024-08-04", "lab_status": "Processing",
             "lab_result": "Footprint sizes: 8, 9, 10. Nike Air sole pattern on size 9."},
            {"description": "CCTV footage — Sarjapur Junction camera", "evidence_type": "Digital",
             "priority": "Critical", "chain_of_custody": "Traffic CCTV → Case file",
             "location_found": "Sarjapur Main Rd junction", "collected_by": "ASI Nagaraj",
             "date_collected": "2024-08-04", "lab_status": "Completed",
             "lab_result": "White Swift Dzire (partial plate: KA-??-HF-??). 3 occupants confirm with footprint count."},
        ]),
        dvi_records=[],
        hotspot_pins=[
            HotspotPin("HP-003-A", "CASE-2024-003", 12.9104, 77.6754, "South-East Zone", "Burglary", "High", "2024-08-04 03:30"),
        ]
    ),

    CaseRecord(
        case_id="CASE-2024-004",
        title="Unidentified Deceased — Ulsoor Lake (DVI Case)",
        status="Active",
        priority="Critical",
        crime_type="Homicide / Unidentified Deceased",
        date_opened="2024-08-12",
        investigating_officer="Inspector Dilip Sharma",
        police_station="Ulsoor Police Station",
        district="Bengaluru Central",
        victim_names=["Unknown Male Deceased (UD-2024-042)"],
        accused_names=["Unknown"],
        location="Ulsoor Lake, Near Boat Club, Bengaluru",
        fir_text="""Police Report — Ulsoor PS
Nature: Unidentified Deceased Person
Date of Discovery: 12/08/2024 at 06:15 Hrs

A partially decomposed male body was recovered from Ulsoor Lake near the boat club by early morning joggers. No identity documents found. Estimated age: 30-40 years. Injuries suggest non-accidental death. Body transferred to Victoria Government Hospital mortuary for post-mortem and DVI procedures.""",
        similar_cases=["CASE-2024-005"],
        investigation_findings="Post-mortem confirms blunt force trauma. DNA profile extracted. Missing persons database cross-match in progress. Fingerprint recovery attempted.",
        last_updated="2024-08-19",
        evidence_items=_make_evidence("CASE-2024-004", [
            {"description": "Post-mortem examination report UD-2024-042", "evidence_type": "Documentary",
             "priority": "Critical", "chain_of_custody": "Victoria Hospital → Ulsoor PS",
             "location_found": "Victoria Government Hospital Mortuary", "collected_by": "Dr. Ananth (Forensic)",
             "date_collected": "2024-08-13", "lab_status": "Completed",
             "lab_result": "Cause of death: Blunt force trauma to occipital region. TOD: 48-72 hrs before recovery."},
            {"description": "Fingerprint lifts from right hand (partial)", "evidence_type": "Biological",
             "priority": "Critical", "chain_of_custody": "Mortuary → AFIS CCTNS",
             "location_found": "Right hand index and middle fingers", "collected_by": "SOCO Fingerprint Expert",
             "date_collected": "2024-08-13", "lab_status": "Processing",
             "lab_result": "8-point partial lift obtained. AFIS query submitted — no hit yet."},
            {"description": "DNA blood sample from deceased", "evidence_type": "Biological",
             "priority": "Critical", "chain_of_custody": "Mortuary → FSL DNA Lab",
             "location_found": "Cardiac blood sample", "collected_by": "Dr. Ananth",
             "date_collected": "2024-08-13", "lab_status": "Processing",
             "lab_result": "DNA profile extracted. Cross-referencing NDNAD missing persons database."},
        ]),
        dvi_records=_make_dvi("CASE-2024-004", [
            {"victim_name": "Unknown Male Deceased (UD-2024-042)",
             "status": "Unidentified",
             "method_used": "Fingerprint + DNA",
             "confidence": 0.0,
             "ante_mortem_ref": "No ante-mortem records found",
             "post_mortem_ref": "PM/2024/VGH/0412",
             "identification_date": "In Progress",
             "examiner": "Dr. Ananth Kumar, Forensic Pathologist",
             "notes": "DNA and fingerprint submitted to national database. Missing persons cross-match pending."},
        ]),
        hotspot_pins=[
            HotspotPin("HP-004-A", "CASE-2024-004", 12.9784, 77.6192, "Central Division", "Homicide", "Critical", "2024-08-12 06:15"),
        ]
    ),

    CaseRecord(
        case_id="CASE-2024-005",
        title="Deepfake Extortion Campaign — IT Professional",
        status="Active",
        priority="High",
        crime_type="Cyber Crime / Deepfake Extortion",
        date_opened="2024-08-18",
        investigating_officer="SI Kavitha Nair",
        police_station="Cyber Crime PS, Bengaluru CID",
        district="Bengaluru Central",
        victim_names=["Arjun Mehta (IT Professional, 32 yrs)"],
        accused_names=["Unknown — Handle: @CryptoBlackHat97"],
        location="Online / Victim resident at Whitefield, Bengaluru",
        fir_text="""Complaint — Cyber Crime PS
Complainant: Arjun Mehta, Age 32, Software Engineer, Whitefield

On 15/08/2024, I received an encrypted message from @CryptoBlackHat97 on Telegram containing a fabricated video of myself in a compromising situation. The video is entirely synthetic/AI-generated. The sender demanded Rs 5 Lakh in crypto within 48 hours or threatened to distribute the video to my employer and social contacts. I have made no such video. The metadata shows digital inconsistencies. I request registration of FIR and immediate action.

Sections: IT Act 67 (Obscene material), IT Act 66C, IPC 384 (Extortion), IPC 507""",
        similar_cases=["CASE-2024-006"],
        investigation_findings="Video analyzed — 97.3% deepfake confidence. Temporal inconsistencies detected in frames 1200-1450. Telegram handle traced to VPN exit node in Eastern Europe. Crypto wallet flagged on INTERPOL watchlist.",
        last_updated="2024-08-25",
        evidence_items=_make_evidence("CASE-2024-005", [
            {"description": "Synthetic video file received via Telegram (.mp4, 47MB)", "evidence_type": "Digital",
             "priority": "Critical", "chain_of_custody": "Complainant → Cyber Cell",
             "location_found": "Telegram encrypted chat download", "collected_by": "SI Kavitha Nair",
             "date_collected": "2024-08-18", "lab_status": "Completed",
             "lab_result": "Deepfake confidence: 97.3%. FaceSwap-GAN artifacts detected. Original source frames from victim's LinkedIn profile."},
            {"description": "Telegram account metadata and IP logs", "evidence_type": "Digital",
             "priority": "Critical", "chain_of_custody": "Telegram (MLAT request)",
             "location_found": "Telegram server logs", "collected_by": "Inspector Mehta",
             "date_collected": "2024-08-22", "lab_status": "Completed",
             "lab_result": "VPN exit node: Bucharest, Romania. Device fingerprint matched to 3 prior extortion complaints."},
            {"description": "Cryptocurrency wallet transaction records", "evidence_type": "Digital",
             "priority": "High", "chain_of_custody": "FIU-IND report",
             "location_found": "Blockchain explorer / FIU-IND", "collected_by": "Cyber Cell",
             "date_collected": "2024-08-23", "lab_status": "Completed",
             "lab_result": "Wallet flagged in INTERPOL I-24/7 for 5 prior cybercrime payouts. Balance: 0.87 ETH."},
        ]),
        deepfake_results=[
            DeepfakeResult(
                analysis_id="DF-2024-001",
                case_id="CASE-2024-005",
                media_type="Video",
                file_description="Extortion video — Telegram download (47MB .mp4)",
                is_manipulated=True,
                confidence_score=97.3,
                detection_model="FaceForensics++ v2 + MesoNet Ensemble",
                manipulation_type="GAN-based FaceSwap with audio synthesis",
                frame_analysis="Frames 1200-1450: inconsistent lighting gradient. Eye-blink pattern: 0.15 Hz (normal: 0.25-0.4 Hz). Compression artifacts in facial boundary region.",
                metadata_flags=["Creation timestamp mismatch", "GPS EXIF stripped", "Software tag: FFmpeg 5.1 (deepfake pipeline indicator)", "Duplicate I-frames at scene transitions"],
                submitted_at="2024-08-19"
            )
        ],
        hotspot_pins=[
            HotspotPin("HP-005-A", "CASE-2024-005", 12.9698, 77.7499, "Whitefield Division", "Cyber Crime", "High", "2024-08-18 00:00"),
        ]
    ),

    CaseRecord(
        case_id="CASE-2024-006",
        title="Fake Courier Pretext Robbery — Senior Citizen Targets",
        status="Active",
        priority="High",
        crime_type="Pretext Robbery / Impersonation",
        date_opened="2024-09-01",
        investigating_officer="SI Aruna Desai",
        police_station="Whitefield Police Station",
        district="Bengaluru East",
        victim_names=["Shailaja Swaminathan (68 yrs)", "Geetha Balakrishnan (71 yrs)"],
        accused_names=["Pradeep @ Sonu", "Unidentified Accomplice (scooter rider)"],
        location="Whitefield / Mahadevapura area, Bengaluru",
        fir_text="""FIR — Whitefield PS
Complainant: Shailaja Swaminathan, 68 yrs

At 1:30 PM a person dressed as courier delivery executive with courier company jacket came with parcel addressed to my son. He asked for water. When I opened the door, he forced entry, brandished a box cutter, threatened me, and forcibly removed my gold bangles and necklace. He escaped on a grey Activa scooter KA-53-EJ-9014 where an accomplice was waiting. He received a call from +91-9741009988 saying 'Hurry up Sonu'.

Sections: IPC 392, IPC 419, IPC 34""",
        similar_cases=["FIR-2024-1508", "FIR-2024-1622"],
        investigation_findings="Grey Activa KA-53-EJ-9014 traced to Pradeep @ Sonu. He is known to Mahadevapura PS. Currently on bail. Two incidents confirm same MO. Arrest warrant issued.",
        last_updated="2024-09-08",
        evidence_items=_make_evidence("CASE-2024-006", [
            {"description": "Dummy Amazon carton used as prop", "evidence_type": "Physical",
             "priority": "High", "chain_of_custody": "SI Desai → Property Room",
             "location_found": "Victim's doorstep — abandoned on escape", "collected_by": "SI Aruna Desai",
             "date_collected": "2024-09-01", "lab_status": "Completed",
             "lab_result": "Fingerprints lifted. 6-point match to Pradeep (known offender, finger-printed at arrest 2023)."},
            {"description": "Courier jacket with logo (partial)", "evidence_type": "Physical",
             "priority": "Medium", "chain_of_custody": "SI Desai → Property Room",
             "location_found": "Abandoned near Whitefield Bus Stop", "collected_by": "PC Suresh",
             "date_collected": "2024-09-03", "lab_status": "Completed",
             "lab_result": "Counterfeit Blue Dart jacket. Fibre matches fibre found on victim's door handle."},
            {"description": "Victim injury photographs and medical certificate", "evidence_type": "Documentary",
             "priority": "High", "chain_of_custody": "Wockhardt Hospital → Case file",
             "location_found": "Wockhardt Hospital, Whitefield", "collected_by": "SI Aruna Desai",
             "date_collected": "2024-09-01", "lab_status": "Completed",
             "lab_result": "Bruising on wrists (restraint). Neck abrasion from chain snatch. Corroborates victim statement."},
        ]),
        hotspot_pins=[
            HotspotPin("HP-006-A", "CASE-2024-006", 12.9791, 77.7526, "Whitefield Division", "Pretext Robbery", "High", "2024-09-01 13:30"),
            HotspotPin("HP-006-B", "CASE-2024-006", 12.9968, 77.7027, "Whitefield Division", "Pretext Robbery", "High", "2024-08-29 14:00"),
        ]
    ),
]

# ─────────────────────────────────────────────────────────────────────
# ACCESS FUNCTIONS
# ─────────────────────────────────────────────────────────────────────

_CASE_DB: Dict[str, CaseRecord] = {c.case_id: c for c in MOCK_CASES}


def get_all_cases() -> List[CaseRecord]:
    return list(_CASE_DB.values())


def get_case(case_id: str) -> Optional[CaseRecord]:
    return _CASE_DB.get(case_id)


def add_case(record: CaseRecord) -> None:
    _CASE_DB[record.case_id] = record


def update_case_field(case_id: str, field_name: str, value: Any) -> bool:
    if case_id in _CASE_DB:
        setattr(_CASE_DB[case_id], field_name, value)
        _CASE_DB[case_id].last_updated = datetime.now().strftime("%Y-%m-%d")
        return True
    return False


def get_active_cases() -> List[CaseRecord]:
    return [c for c in _CASE_DB.values() if c.status == "Active"]


def get_cases_by_type(crime_type: str) -> List[CaseRecord]:
    return [c for c in _CASE_DB.values() if crime_type.lower() in c.crime_type.lower()]


def get_dvi_cases() -> List[CaseRecord]:
    return [c for c in _CASE_DB.values() if c.dvi_records]


def get_deepfake_cases() -> List[CaseRecord]:
    return [c for c in _CASE_DB.values() if c.deepfake_results]


def stats_summary() -> Dict[str, Any]:
    all_c = get_all_cases()
    all_ev = [ev for c in all_c for ev in c.evidence_items]
    all_dvi = [dv for c in all_c for dv in c.dvi_records]
    return {
        "total_cases": len(all_c),
        "active_cases": len([c for c in all_c if c.status == "Active"]),
        "critical_cases": len([c for c in all_c if c.priority == "Critical"]),
        "total_evidence": len(all_ev),
        "critical_evidence": len([e for e in all_ev if e.priority == "Critical"]),
        "dvi_cases": len([c for c in all_c if c.dvi_records]),
        "deepfake_cases": len([c for c in all_c if c.deepfake_results]),
        "cases_with_hotspots": len([c for c in all_c if c.hotspot_pins]),
        "evidence_pending": len([e for e in all_ev if e.lab_status == "Pending"]),
        "evidence_processing": len([e for e in all_ev if e.lab_status == "Processing"]),
    }
