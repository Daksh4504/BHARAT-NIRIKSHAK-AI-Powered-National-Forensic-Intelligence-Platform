"""
ICIIP — Central Mock Data Store
All UI pages import from here. No backend logic lives here — only data shapes.

When integrating real functions, replace the relevant section in this file
or have pages call the real function directly and stop importing from here.
"""

from __future__ import annotations
from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────────────
# CASE REGISTRY (used by sidebar, cases page, dashboard)
# TODO: replace with real_case_database.get_all_cases()
# ─────────────────────────────────────────────────────────────────────
CASES: List[Dict[str, Any]] = [
    {
        "case_id": "CASE-2024-001",
        "title": "Old Airport Road Chain Snatching Series",
        "status": "Active", "priority": "Critical",
        "crime_type": "Snatching / Robbery",
        "date_opened": "2024-07-15", "last_updated": "2024-07-22",
        "investigating_officer": "SI Ramesh Kumar",
        "police_station": "HAL Police Station, Bengaluru",
        "district": "Bengaluru East",
        "location": "Old Airport Road / Koramangala corridor, Bengaluru",
        "victim_names": ["Meenakshi Sundaram", "Kavita Rao", "Sunita Rao"],
        "accused_names": ["Bunty @ Rakesh", "Kallu @ Vikram"],
        "similar_cases": ["FIR-2024-0812", "FIR-2024-0945", "FIR-2024-1750"],
        "investigation_findings": "Suspect vehicle KA-03-HX-4812 traced to Bunty @ Rakesh. Three linked incidents across East and South Zone. ANPR alerts active.",
        "fir_text": "On 15/07/2024 at 20:00 hrs, two men on a Black Bajaj Pulsar KA-03-HX-4812 snatched 32g gold chain near Manipal Hospital Bus Stop, Old Airport Road. Pillion wore red helmet.",
        "evidence_count": 4, "dvi_count": 0, "deepfake_count": 0, "hotspot_count": 3,
    },
    {
        "case_id": "CASE-2024-002",
        "title": "BESCOM APK Phishing Fraud Ring",
        "status": "Active", "priority": "High",
        "crime_type": "Cyber Fraud / Financial Scam",
        "date_opened": "2024-07-20", "last_updated": "2024-07-28",
        "investigating_officer": "SI Pooja Iyer",
        "police_station": "Cyber Crime PS, Bengaluru CID",
        "district": "Bengaluru Central",
        "location": "Online — Victims across Indiranagar, Jayanagar, Malleshwaram",
        "victim_names": ["Dr. Harish Chandra", "Venkatesh Murthy", "Anand Kulkarni"],
        "accused_names": ["Manoj Kumar @ Rajat", "Ramesh Shah (Mule)"],
        "similar_cases": ["FIR-2024-1102", "FIR-2024-1240"],
        "investigation_findings": "+91-9876543210 traced to Jamtara, Jharkhand. CDR shows 47 calls. Mule account frozen. Rs 1.2L recovered.",
        "fir_text": "Received fake SMS claiming electricity disconnection. Called +91-9876543210. Installed BESCOM_QuickPay.apk. Rs 5.2L debited in 3 RTGS transactions.",
        "evidence_count": 3, "dvi_count": 0, "deepfake_count": 0, "hotspot_count": 1,
    },
    {
        "case_id": "CASE-2024-003",
        "title": "Rainbow Layout Villa Burglary — Sarjapur Road",
        "status": "Active", "priority": "High",
        "crime_type": "House Burglary / Breaking by Night",
        "date_opened": "2024-08-04", "last_updated": "2024-08-10",
        "investigating_officer": "ASI Nagaraj B",
        "police_station": "Bellandur Police Station",
        "district": "Bengaluru South-East",
        "location": "Rainbow Residential Layout, Sarjapur Main Road",
        "victim_names": ["Vikramaditya Sen"],
        "accused_names": ["Iron Rod Syndicate (3 masked men)"],
        "similar_cases": ["FIR-2024-1315", "FIR-2024-1420"],
        "investigation_findings": "White Swift Dzire traced to fake registration. Syndicate believed to be 4-5 members from Tumkur.",
        "fir_text": "Family returned from holiday to find villa burglarized. Rear grill cut with hydraulic bolt cutter. Stolen: Gold 120g, Cash Rs 3L, 2 Swiss watches.",
        "evidence_count": 3, "dvi_count": 0, "deepfake_count": 0, "hotspot_count": 1,
    },
    {
        "case_id": "CASE-2024-004",
        "title": "Unidentified Deceased — Ulsoor Lake (DVI Case)",
        "status": "Active", "priority": "Critical",
        "crime_type": "Homicide / Unidentified Deceased",
        "date_opened": "2024-08-12", "last_updated": "2024-08-19",
        "investigating_officer": "Inspector Dilip Sharma",
        "police_station": "Ulsoor Police Station",
        "district": "Bengaluru Central",
        "location": "Ulsoor Lake, Near Boat Club, Bengaluru",
        "victim_names": ["Unknown Male Deceased (UD-2024-042)"],
        "accused_names": ["Unknown"],
        "similar_cases": ["CASE-2024-005"],
        "investigation_findings": "Post-mortem confirms blunt force trauma. DNA profile extracted. Fingerprint AFIS query pending.",
        "fir_text": "Male body recovered from Ulsoor Lake at 06:15 hrs. No identity documents. Estimated age 30-40 yrs. Injuries suggest non-accidental death.",
        "evidence_count": 3, "dvi_count": 1, "deepfake_count": 0, "hotspot_count": 1,
    },
    {
        "case_id": "CASE-2024-005",
        "title": "Deepfake Extortion Campaign — IT Professional",
        "status": "Active", "priority": "High",
        "crime_type": "Cyber Crime / Deepfake Extortion",
        "date_opened": "2024-08-18", "last_updated": "2024-08-25",
        "investigating_officer": "SI Kavitha Nair",
        "police_station": "Cyber Crime PS, Bengaluru CID",
        "district": "Bengaluru Central",
        "location": "Online — Victim at Whitefield, Bengaluru",
        "victim_names": ["Arjun Mehta (IT Professional, 32 yrs)"],
        "accused_names": ["Unknown — Handle: @CryptoBlackHat97"],
        "similar_cases": ["CASE-2024-006"],
        "investigation_findings": "Video 97.3% deepfake confidence. Telegram handle traced to VPN exit node, Bucharest. Crypto wallet on INTERPOL watchlist.",
        "fir_text": "Received synthetic video via Telegram. Extortion demand Rs 5L in crypto. Metadata shows GAN-based FaceSwap artifacts.",
        "evidence_count": 3, "dvi_count": 0, "deepfake_count": 1, "hotspot_count": 1,
    },
    {
        "case_id": "CASE-2024-006",
        "title": "Fake Courier Pretext Robbery — Senior Citizen Targets",
        "status": "Active", "priority": "High",
        "crime_type": "Pretext Robbery / Impersonation",
        "date_opened": "2024-09-01", "last_updated": "2024-09-08",
        "investigating_officer": "SI Aruna Desai",
        "police_station": "Whitefield Police Station",
        "district": "Bengaluru East",
        "location": "Whitefield / Mahadevapura area, Bengaluru",
        "victim_names": ["Shailaja Swaminathan (68 yrs)", "Geetha Balakrishnan (71 yrs)"],
        "accused_names": ["Pradeep @ Sonu", "Unidentified Accomplice"],
        "similar_cases": ["FIR-2024-1508", "FIR-2024-1622"],
        "investigation_findings": "Grey Activa KA-53-EJ-9014 traced to Pradeep @ Sonu. Arrest warrant issued.",
        "fir_text": "Person dressed as courier executive asked for water. Forced entry, brandished box cutter, robbed gold bangles. Escaped on grey Activa KA-53-EJ-9014.",
        "evidence_count": 3, "dvi_count": 0, "deepfake_count": 0, "hotspot_count": 2,
    },
]

# Quick lookup
CASES_BY_ID: Dict[str, Dict] = {c["case_id"]: c for c in CASES}

# ─────────────────────────────────────────────────────────────────────
# EVIDENCE ITEMS
# TODO: replace with evidence_module.get_all_evidence()
# ─────────────────────────────────────────────────────────────────────
EVIDENCE: List[Dict[str, Any]] = [
    {"evidence_id":"EV-001","case_id":"CASE-2024-001","description":"CCTV footage — Manipal Hospital junction cam #7","evidence_type":"Digital","priority":"Critical","lab_status":"Completed","lab_result":"KA-03-HX-4812 confirmed. Face partially visible.","collected_by":"SI Ramesh Kumar","date_collected":"2024-07-15","location_found":"Old Airport Road Camera #7","chain_of_custody":"SI Kumar → SOCO Lab"},
    {"evidence_id":"EV-002","case_id":"CASE-2024-001","description":"Gold chain fragment (8g) recovered from footpath","evidence_type":"Physical","priority":"High","lab_status":"Completed","lab_result":"22K gold. Matches victim's jeweller records.","collected_by":"PC Venkat","date_collected":"2024-07-15","location_found":"Near bus stop footpath","chain_of_custody":"Beat constable → Property Room"},
    {"evidence_id":"EV-003","case_id":"CASE-2024-001","description":"Witness statement — auto driver Raju M","evidence_type":"Documentary","priority":"High","lab_status":"Completed","lab_result":"Corroborates vehicle and suspect description.","collected_by":"SI Ramesh Kumar","date_collected":"2024-07-16","location_found":"Old Airport Road","chain_of_custody":"SI Kumar → Case File"},
    {"evidence_id":"EV-004","case_id":"CASE-2024-001","description":"Fingerprint swab from lamppost","evidence_type":"Biological","priority":"Medium","lab_status":"Processing","lab_result":"Awaiting AFIS match.","collected_by":"SOCO Officer Priya","date_collected":"2024-07-16","location_found":"Lamppost near snatching site","chain_of_custody":"SOCO → FSL Bengaluru"},
    {"evidence_id":"EV-005","case_id":"CASE-2024-002","description":"Malicious APK — BESCOM_QuickPay_Update.apk","evidence_type":"Digital","priority":"Critical","lab_status":"Completed","lab_result":"AnyDesk-based screen-mirroring RAT/FraudBridge payload.","collected_by":"SI Pooja Iyer","date_collected":"2024-07-20","location_found":"Victim's mobile phone","chain_of_custody":"Victim → Cyber Cell"},
    {"evidence_id":"EV-006","case_id":"CASE-2024-002","description":"CDR for +91-9876543210","evidence_type":"Digital","priority":"Critical","lab_status":"Completed","lab_result":"47 victim calls. Tower: Jamtara, Jharkhand.","collected_by":"Inspector Mehta","date_collected":"2024-07-23","location_found":"Telecom server (TRAI requisition)","chain_of_custody":"Telecom operator → Cyber Cell"},
    {"evidence_id":"EV-007","case_id":"CASE-2024-002","description":"Bank statements — Ramesh Shah mule account","evidence_type":"Documentary","priority":"High","lab_status":"Completed","lab_result":"Rs 3.2L frozen. Onward transfer to 4 crypto wallets.","collected_by":"Inspector Mehta","date_collected":"2024-07-24","location_found":"SBI Branch Jamtara","chain_of_custody":"SBI Legal → Cyber Cell"},
    {"evidence_id":"EV-008","case_id":"CASE-2024-003","description":"Hydraulic bolt cutter blade fragment","evidence_type":"Physical","priority":"Critical","lab_status":"Completed","lab_result":"Industrial grade. Tool marks match FIR-2024-1315.","collected_by":"SOCO Team","date_collected":"2024-08-04","location_found":"Rear kitchen window sill","chain_of_custody":"ASI Nagaraj → FSL"},
    {"evidence_id":"EV-009","case_id":"CASE-2024-003","description":"Footprint casts (3 suspects, rear boundary wall)","evidence_type":"Physical","priority":"High","lab_status":"Processing","lab_result":"Sizes 8, 9, 10. Nike Air sole pattern on size 9.","collected_by":"SOCO Officer Priya","date_collected":"2024-08-04","location_found":"Rear boundary wall","chain_of_custody":"SOCO → FSL"},
    {"evidence_id":"EV-010","case_id":"CASE-2024-003","description":"CCTV footage — Sarjapur Junction camera","evidence_type":"Digital","priority":"Critical","lab_status":"Completed","lab_result":"White Swift Dzire. 3 occupants confirmed.","collected_by":"ASI Nagaraj","date_collected":"2024-08-04","location_found":"Sarjapur Main Rd junction","chain_of_custody":"Traffic CCTV → Case file"},
    {"evidence_id":"EV-011","case_id":"CASE-2024-004","description":"Post-mortem report UD-2024-042","evidence_type":"Documentary","priority":"Critical","lab_status":"Completed","lab_result":"Blunt force trauma to occipital. TOD: 48-72 hrs before recovery.","collected_by":"Dr. Ananth (Forensic)","date_collected":"2024-08-13","location_found":"Victoria Government Hospital Mortuary","chain_of_custody":"Victoria Hospital → Ulsoor PS"},
    {"evidence_id":"EV-012","case_id":"CASE-2024-004","description":"Fingerprint lifts — right hand (partial)","evidence_type":"Biological","priority":"Critical","lab_status":"Processing","lab_result":"8-point partial lift. AFIS query submitted — no hit yet.","collected_by":"SOCO Fingerprint Expert","date_collected":"2024-08-13","location_found":"Right hand index/middle fingers","chain_of_custody":"Mortuary → AFIS CCTNS"},
    {"evidence_id":"EV-013","case_id":"CASE-2024-004","description":"DNA blood sample from deceased","evidence_type":"Biological","priority":"Critical","lab_status":"Processing","lab_result":"DNA profile extracted. NDNAD cross-match in progress.","collected_by":"Dr. Ananth","date_collected":"2024-08-13","location_found":"Cardiac blood sample","chain_of_custody":"Mortuary → FSL DNA Lab"},
    {"evidence_id":"EV-014","case_id":"CASE-2024-005","description":"Extortion video (.mp4, 47MB) via Telegram","evidence_type":"Digital","priority":"Critical","lab_status":"Completed","lab_result":"Deepfake confidence 97.3%. FaceSwap-GAN artifacts. Source: victim LinkedIn.","collected_by":"SI Kavitha Nair","date_collected":"2024-08-18","location_found":"Telegram encrypted chat","chain_of_custody":"Complainant → Cyber Cell"},
    {"evidence_id":"EV-015","case_id":"CASE-2024-005","description":"Telegram account metadata and IP logs","evidence_type":"Digital","priority":"Critical","lab_status":"Completed","lab_result":"VPN exit node: Bucharest, Romania. Device matched 3 prior extortion cases.","collected_by":"Inspector Mehta","date_collected":"2024-08-22","location_found":"Telegram server logs (MLAT)","chain_of_custody":"Telegram → MLAT"},
    {"evidence_id":"EV-016","case_id":"CASE-2024-005","description":"Crypto wallet transaction records","evidence_type":"Digital","priority":"High","lab_status":"Completed","lab_result":"Wallet flagged INTERPOL I-24/7. Balance: 0.87 ETH.","collected_by":"Cyber Cell","date_collected":"2024-08-23","location_found":"Blockchain explorer / FIU-IND","chain_of_custody":"FIU-IND report"},
    {"evidence_id":"EV-017","case_id":"CASE-2024-006","description":"Dummy Amazon carton used as prop","evidence_type":"Physical","priority":"High","lab_status":"Completed","lab_result":"Fingerprints: 6-point match to Pradeep (known offender).","collected_by":"SI Aruna Desai","date_collected":"2024-09-01","location_found":"Victim's doorstep","chain_of_custody":"SI Desai → Property Room"},
    {"evidence_id":"EV-018","case_id":"CASE-2024-006","description":"Counterfeit Blue Dart courier jacket","evidence_type":"Physical","priority":"Medium","lab_status":"Completed","lab_result":"Fibre matches fibre on victim's door handle.","collected_by":"PC Suresh","date_collected":"2024-09-03","location_found":"Abandoned near Whitefield Bus Stop","chain_of_custody":"PC Suresh → Property Room"},
    {"evidence_id":"EV-019","case_id":"CASE-2024-006","description":"Victim injury photographs and medical certificate","evidence_type":"Documentary","priority":"High","lab_status":"Completed","lab_result":"Bruising on wrists (restraint). Neck abrasion corroborates statement.","collected_by":"SI Aruna Desai","date_collected":"2024-09-01","location_found":"Wockhardt Hospital, Whitefield","chain_of_custody":"Wockhardt Hospital → Case file"},
]

# ─────────────────────────────────────────────────────────────────────
# DVI RECORDS
# TODO: replace with dvi_module.get_all_dvi_records()
# ─────────────────────────────────────────────────────────────────────
DVI_RECORDS: List[Dict[str, Any]] = [
    {"dvi_id":"DVI-001","case_id":"CASE-2024-004","victim_name":"Unknown Male Deceased (UD-2024-042)","status":"Unidentified","method_used":"Fingerprint + DNA","confidence":0.0,"ante_mortem_ref":"No ante-mortem records found","post_mortem_ref":"PM/2024/VGH/0412","identification_date":"In Progress","examiner":"Dr. Ananth Kumar, Forensic Pathologist","notes":"DNA and fingerprint submitted to national database. Missing persons cross-match pending."},
]

# ─────────────────────────────────────────────────────────────────────
# DEEPFAKE RESULTS
# TODO: replace with deepfake_module.get_all_results()
# ─────────────────────────────────────────────────────────────────────
DEEPFAKE_RESULTS: List[Dict[str, Any]] = [
    {"analysis_id":"DF-2024-001","case_id":"CASE-2024-005","media_type":"Video","file_description":"Extortion video — Telegram download (47MB .mp4)","is_manipulated":True,"confidence_score":97.3,"detection_model":"FaceForensics++ v2 + MesoNet Ensemble","manipulation_type":"GAN-based FaceSwap with audio synthesis","frame_analysis":"Frames 1200-1450: inconsistent lighting gradient. Eye-blink: 0.15 Hz (normal: 0.25-0.4 Hz). Compression artifacts at facial boundary.","metadata_flags":["Creation timestamp mismatch","GPS EXIF stripped","Software tag: FFmpeg 5.1 (deepfake pipeline)","Duplicate I-frames at scene transitions"],"submitted_at":"2024-08-19"},
]

# ─────────────────────────────────────────────────────────────────────
# HOTSPOT PINS
# TODO: replace with hotspot_module.get_all_pins()
# ─────────────────────────────────────────────────────────────────────
HOTSPOT_PINS: List[Dict[str, Any]] = [
    {"pin_id":"HP-001","case_id":"CASE-2024-001","lat":12.9716,"lon":77.5946,"zone":"East Zone","crime_type":"Snatching / Robbery","severity":"High","timestamp":"2024-07-15 20:00"},
    {"pin_id":"HP-002","case_id":"CASE-2024-001","lat":12.9279,"lon":77.6271,"zone":"South-East Zone","crime_type":"Snatching / Robbery","severity":"High","timestamp":"2024-03-28 20:15"},
    {"pin_id":"HP-003","case_id":"CASE-2024-001","lat":12.9254,"lon":77.5840,"zone":"South Zone","crime_type":"Snatching / Robbery","severity":"Medium","timestamp":"2024-06-10 20:30"},
    {"pin_id":"HP-004","case_id":"CASE-2024-002","lat":12.9667,"lon":77.6430,"zone":"Cyber Crime Jurisdiction","crime_type":"Cyber Fraud","severity":"High","timestamp":"2024-07-20 11:00"},
    {"pin_id":"HP-005","case_id":"CASE-2024-003","lat":12.9104,"lon":77.6754,"zone":"South-East Zone","crime_type":"Burglary","severity":"High","timestamp":"2024-08-04 03:30"},
    {"pin_id":"HP-006","case_id":"CASE-2024-004","lat":12.9784,"lon":77.6192,"zone":"Central Division","crime_type":"Homicide","severity":"Critical","timestamp":"2024-08-12 06:15"},
    {"pin_id":"HP-007","case_id":"CASE-2024-005","lat":12.9698,"lon":77.7499,"zone":"Whitefield Division","crime_type":"Cyber Crime","severity":"High","timestamp":"2024-08-18 00:00"},
    {"pin_id":"HP-008","case_id":"CASE-2024-006","lat":12.9791,"lon":77.7526,"zone":"Whitefield Division","crime_type":"Pretext Robbery","severity":"High","timestamp":"2024-09-01 13:30"},
    {"pin_id":"HP-009","case_id":"CASE-2024-006","lat":12.9968,"lon":77.7027,"zone":"Whitefield Division","crime_type":"Pretext Robbery","severity":"High","timestamp":"2024-08-29 14:00"},
]

# ─────────────────────────────────────────────────────────────────────
# FIR INTELLIGENCE — MOCK NLP EXTRACTION RESULT
# TODO: replace with fir_module.extract_entities_from_text(fir_text)
# ─────────────────────────────────────────────────────────────────────
FIR_SAMPLE_TEXT = """FIRST INFORMATION REPORT
Police Station: HAL Police Station, Bengaluru City
Date & Time of Occurrence: 15/07/2024 at 20:00 Hrs
Place of Occurrence: Near Manipal Hospital Bus Stop, Old Airport Road, Bengaluru

Complainant: Mrs. Meenakshi Sundaram, Aged 46 years

At around 8:00 PM, two unknown men on a high-speed black Bajaj Pulsar motorcycle KA-03-HX-4812 approached me from behind. The pillion rider (red helmet) forcefully snatched my 24-carat gold chain weighing 32 grams (Rs. 2,10,000) from my neck. They sped towards Marathahalli flyover.

Sections: IPC 392 (Robbery), IPC 34"""

FIR_EXTRACTED = {
    "case_id": "CASE-2024-001",
    "police_station": "HAL Police Station, Bengaluru",
    "date_time": "15/07/2024 at 20:00 Hrs",
    "crime_type": "Snatching / Robbery",
    "legal_sections": ["IPC 392 (Robbery)", "IPC 34 (Common Intention)"],
    "complainant": "Mrs. Meenakshi Sundaram",
    "victims": ["Meenakshi Sundaram"],
    "accused_suspects": ["Bunty @ Rakesh (Driver)", "Kallu @ Vikram (Pillion, red helmet)"],
    "location": "Old Airport Road, near Manipal Hospital Bus Stop, Bengaluru",
    "city_zone": "East Zone",
    "modus_operandi": "Approach from blind spot on Black Bajaj Pulsar. Pillion snatched gold chain at speed. Fled via Marathahalli flyover at 20:00 hrs.",
    "mo_pretext_trick": "None / Direct surprise snatch-and-run",
    "mo_entry_exit": "Pedestrian sidewalk approach, rapid motorcycle acceleration",
    "mo_transport": "Black Bajaj Pulsar 220 (KA-03-HX-4812)",
    "mo_timing_profile": "Evening Rush / Dusk (19:30 – 21:30 Hrs)",
    "mo_target_profile": "Lone Female Pedestrian / Commuter",
    "weapons": ["None displayed (Physical force)"],
    "vehicles_involved": ["KA-03-HX-4812 (Black Bajaj Pulsar)"],
    "stolen_property": ["24K Gold Chain, 32g, valued Rs 2,10,000"],
    "phone_numbers": [],
}

# ─────────────────────────────────────────────────────────────────────
# FIR HISTORICAL MATCHES
# TODO: replace with fir_module.compare_fir_against_historical(extracted)
# ─────────────────────────────────────────────────────────────────────
FIR_HISTORICAL_MATCHES = [
    {"case_id":"FIR-2024-0945","police_station":"Koramangala PS","date_time":"2024-03-28 20:15","crime_type":"Snatching / Robbery","location":"5th Block, Koramangala","accused":["Bunty @ Rakesh","Kallu @ Vikram"],"modus_operandi":"Black Pulsar KA-03-HX-4812. Pillion red helmet brandished knife at female pedestrian.","overall_score":94.0,"mo_similarity":88.0,"entity_overlap":95.0,"crime_type_match":100.0,"location_proximity":72.0,"matched_features":["Identical Vehicle: KA-03-HX-4812","Suspect Alias Match: Bunty @ Rakesh","Suspect Alias Match: Kallu @ Vikram"],"notes":"High probability pattern correlation. Strong tangible entity cross-match."},
    {"case_id":"FIR-2024-0812","police_station":"Indiranagar PS","date_time":"2024-03-12 19:45","crime_type":"Snatching / Robbery","location":"100 Feet Road, CMH Junction","accused":["Bunty @ Rakesh","Kallu @ Vikram (Pillion)"],"modus_operandi":"Black Pulsar no front plate. Red helmet pillion grabbed gold mangalsutra.","overall_score":89.0,"mo_similarity":85.0,"entity_overlap":80.0,"crime_type_match":100.0,"location_proximity":68.0,"matched_features":["Suspect Alias Match: Bunty @ Rakesh","Vehicle Characteristic: Black Pulsar 4812"],"notes":"Identical tactical MO. Same suspect aliases."},
    {"case_id":"FIR-2024-1750","police_station":"Jayanagar PS","date_time":"2024-06-10 20:30","crime_type":"Snatching / Robbery","location":"4th Block, near Cool Joint, Jayanagar","accused":["Bunty @ Rakesh","Kallu @ Vikram"],"modus_operandi":"Black Pulsar KA-03-HX-4812. Pillion red helmet snatched gold chain at bus stop.","overall_score":92.0,"mo_similarity":90.0,"entity_overlap":90.0,"crime_type_match":100.0,"location_proximity":65.0,"matched_features":["Identical Vehicle: KA-03-HX-4812","Suspect Alias Match: Bunty @ Rakesh"],"notes":"High probability. Same vehicle, same suspects."},
    {"case_id":"FIR-2024-1315","police_station":"HSR Layout PS","date_time":"2024-04-22 03:15","crime_type":"House Burglary","location":"Sector 2, HSR Layout","accused":["Chaddi Baniyan Gang (3 unidentified)"],"modus_operandi":"Bolt cutter entry, white Swift Dzire getaway.","overall_score":38.0,"mo_similarity":22.0,"entity_overlap":10.0,"crime_type_match":15.0,"location_proximity":55.0,"matched_features":[],"notes":"Low contextual similarity — different crime typology."},
    {"case_id":"FIR-2024-1622","police_station":"Mahadevapura PS","date_time":"2024-05-29 14:00","crime_type":"Pretext Robbery","location":"Garudachar Palya, Mahadevapura","accused":["Pradeep @ Sonu"],"modus_operandi":"Courier pretext, box cutter, grey Activa.","overall_score":31.0,"mo_similarity":18.0,"entity_overlap":5.0,"crime_type_match":15.0,"location_proximity":48.0,"matched_features":[],"notes":"Different MO class — included for geographic proximity."},
]

# ─────────────────────────────────────────────────────────────────────
# REPEAT OFFENDER INDICATORS
# TODO: replace with fir_module.detect_repeat_offender_signatures(...)
# ─────────────────────────────────────────────────────────────────────
REPEAT_OFFENDER_INDICATORS = [
    {"suspect_or_cluster":"Serial Transport Signature (KA-03-HX-4812)","confidence_level":"HIGH","match_type":"Vehicle Registration & Getaway Match","risk_level":"High Pattern Recurrence","evidence_reasoning":["Registration KA-03-HX-4812 confirmed in current FIR.","Same vehicle in FIR-2024-0945 (Koramangala PS, 28/03/2024).","Same vehicle in FIR-2024-1750 (Jayanagar PS, 10/06/2024).","Consistent red-helmet pillion rider configuration in all incidents."],"linked_case_ids":["CASE-2024-001","FIR-2024-0945","FIR-2024-1750"],"recommended_action":"Alert ANPR cameras for KA-03-HX-4812 across all toll gates. Inspect RTO ownership records. Coordinate with Koramangala and Jayanagar PS IOs."},
    {"suspect_or_cluster":"Known Offender: Bunty @ Rakesh","confidence_level":"HIGH","match_type":"Direct Identity / Alias Match","risk_level":"High Pattern Recurrence","evidence_reasoning":["Alias 'Bunty @ Rakesh' matches known offender in FIR-2024-0812 and FIR-2024-0945.","Three confirmed incidents across East Zone corridor within 3 months.","Operating with consistent accomplice Kallu @ Vikram (pillion)."],"linked_case_ids":["CASE-2024-001","FIR-2024-0812","FIR-2024-0945"],"recommended_action":"Pull history-sheet for Bunty @ Rakesh. Verify bail/parole status at Central Prison. Deploy informers in known associate locations."},
    {"suspect_or_cluster":"East-South Corridor Bike Snatching Series","confidence_level":"HIGH","match_type":"Signature MO & Tactical Footprint","risk_level":"Emerging MO Pattern","evidence_reasoning":["MO match score 90% with FIR-2024-1750.","Entry method identical: pedestrian approach from blind spot.","Timing consistent: Evening 19:30–21:30 across all incidents.","Target profile consistent: lone female commuter."],"linked_case_ids":["CASE-2024-001","FIR-2024-0945","FIR-2024-1750","FIR-2024-0812"],"recommended_action":"Consolidated CCTV review along 100 Ft Rd → Koramangala 5th Block → Jayanagar corridor. Night patrol escalation 19:00–22:00."},
]

# ─────────────────────────────────────────────────────────────────────
# CRIME TREND DATA
# TODO: replace with fir_module.analyze_crime_trends(all_firs)
# ─────────────────────────────────────────────────────────────────────
CRIME_TREND_DATA = {
    "total_cases": 11,
    "category_counts": {"Snatching / Robbery": 5, "Cyber Fraud": 3, "House Burglary": 2, "Pretext Robbery": 1},
    "zone_counts": {"East Zone": 4, "South-East Zone": 3, "Whitefield Division": 2, "Cyber Cell": 1, "South Zone": 1},
    "time_bins": {"Late Night (00:00–05:00)": 2, "Morning (05:00–11:00)": 1, "Afternoon (11:00–16:00)": 2, "Evening/Dusk (16:00–20:00)": 1, "Night Prime (20:00–24:00)": 5},
    "active_series": [
        {"series_name":"East-South Corridor Bike Snatching","signature":"Black Pulsar KA-03-HX-4812, red helmet pillion, lone female target, 19:30–21:30 hrs","linked_cases":["CASE-2024-001","FIR-2024-0812","FIR-2024-0945","FIR-2024-1750"],"threat_level":"CRITICAL — Active Daily Recurrence","recommended_patrol":"Intensive motorcycle patrol on 100 Ft Rd, Old Airport Rd, Koramangala 5th Block 19:00–22:00."},
        {"series_name":"BESCOM APK Phishing Ring","signature":"Phishing SMS → WhatsApp APK → RTGS siphoning → Jamtara syndicate","linked_cases":["CASE-2024-002","FIR-2024-1102","FIR-2024-1240"],"threat_level":"HIGH — Cross-City Financial Damage","recommended_patrol":"Issue public advisory. Freeze beneficiary mule accounts. CDR analysis."},
        {"series_name":"Villa Night Burglary Syndicate","signature":"Hydraulic bolt cutter rear grill, 02:30–04:00 AM, locked residences, white Swift Dzire","linked_cases":["CASE-2024-003","FIR-2024-1315","FIR-2024-1420"],"threat_level":"ELEVATED — Intermittent Strikes","recommended_patrol":"Naka checking on Outer Ring Road and Sarjapur junction for white Swift cars."},
        {"series_name":"Fake Delivery Pretext Robbery","signature":"Courier uniform + dummy carton, box cutter, senior citizen target, afternoon","linked_cases":["CASE-2024-006","FIR-2024-1508","FIR-2024-1622"],"threat_level":"HIGH — Physical Risk to Seniors","recommended_patrol":"Gated society security guards to verify courier ID. Stop unannounced deliveries."},
    ],
}

# ─────────────────────────────────────────────────────────────────────
# INVESTIGATION DOSSIER ACTIONS
# TODO: replace with fir_module.generate_investigator_action_items(...)
# ─────────────────────────────────────────────────────────────────────
DOSSIER_ACTIONS = [
    {"category":"Surveillance & ANPR Alert","priority":"HIGH","task":"Broadcast ANPR flash alert for KA-03-HX-4812 across all city toll gates, traffic junctions, and bordering check-posts.","statutory_ref":"Section 91 CrPC"},
    {"category":"Repeat Offender Verification","priority":"CRITICAL","task":"Pull history-sheet for Bunty @ Rakesh and Kallu @ Vikram. Verify jail/bail status at Central Prison. Deploy local intelligence informers.","statutory_ref":"Habitual Offenders Act & Police Manual"},
    {"category":"Inter-Station IO Coordination","priority":"MEDIUM","task":"Establish formal intelligence liaison with SHO of Koramangala PS (FIR-2024-0945) and Jayanagar PS (FIR-2024-1750).","statutory_ref":"Inter-District Crime Intelligence Circular"},
    {"category":"Forensic & Fingerprint","priority":"HIGH","task":"Chase AFIS result for fingerprint lift EV-004. Retrieve additional CCTV within 500m radius of Old Airport Road incident.","statutory_ref":"FSL Protocol"},
    {"category":"Victim & Witness Support","priority":"STANDARD","task":"Schedule TIP before Executive Magistrate once suspects are apprehended. Provide safety updates to complainant Mrs. Meenakshi Sundaram.","statutory_ref":"Section 54A CrPC"},
]

DOSSIER_TEXT = """
================================================================================
POLICE INTELLIGENCE & CRIME PATTERN DOSSIER
CASE FILE: CASE-2024-001 | PS: HAL Police Station, Bengaluru
================================================================================

LEGAL NOTICE: This system is an automated Investigation Decision-Support Tool.
All pattern matches require independent verification under CrPC / BNSS.

SECTION 1: INCIDENT SUMMARY
  Case ID         : CASE-2024-001
  Date & Time     : 15/07/2024 at 20:00 Hrs
  Crime Type      : Snatching / Robbery
  Legal Sections  : IPC 392, IPC 34
  Location        : Old Airport Road, near Manipal Hospital Bus Stop (East Zone)
  Complainant     : Mrs. Meenakshi Sundaram
  Suspects        : Bunty @ Rakesh, Kallu @ Vikram
  Vehicles        : KA-03-HX-4812 (Black Bajaj Pulsar)

SECTION 2: MODUS OPERANDI
  Full MO         : Blind-spot approach on Black Bajaj Pulsar. Pillion snatched gold chain at speed. Fled via Marathahalli flyover.
  Pretext         : None / Direct snatch-and-run
  Timing          : Evening Rush / Dusk (19:30-21:30 Hrs)
  Target Profile  : Lone Female Pedestrian / Commuter

SECTION 3: HISTORICAL CORRELATIONS
  [1] FIR-2024-0945 (Koramangala PS) — Overall: 94.0%
      Matched: Identical vehicle KA-03-HX-4812 + suspect aliases
  [2] FIR-2024-0812 (Indiranagar PS) — Overall: 89.0%
      Matched: Suspect aliases Bunty @ Rakesh
  [3] FIR-2024-1750 (Jayanagar PS) — Overall: 92.0%
      Matched: Same vehicle + same suspects

SECTION 4: REPEAT OFFENDER INDICATORS
  [!] Serial Transport Signature KA-03-HX-4812 (HIGH CONFIDENCE)
      Linked FIRs: CASE-2024-001, FIR-2024-0945, FIR-2024-1750

SECTION 5: OPERATIONAL ACTIONS FOR IO
  [CRITICAL] Repeat Offender Verification — Pull history-sheets for known suspects
  [HIGH] ANPR Alert — Broadcast flash for KA-03-HX-4812
  [MEDIUM] Inter-Station Coordination — Liaison with Koramangala and Jayanagar PS

================================================================================
END OF DOSSIER — FOR POLICE OFFICIAL USE ONLY
================================================================================
""".strip()

# ─────────────────────────────────────────────────────────────────────
# HISTORICAL FIR REPOSITORY TABLE
# TODO: replace with fir_module.get_all_historical_firs()
# ─────────────────────────────────────────────────────────────────────
FIR_REPOSITORY = [
    {"Case ID":"FIR-2024-0812","PS":"Indiranagar PS","Date":"2024-03-12 19:45","Crime":"Snatching / Robbery","Suspects":"Bunty @ Rakesh, Kallu @ Vikram","Vehicles":"Black Bajaj Pulsar (partial 4812)","Zone":"East Zone"},
    {"Case ID":"FIR-2024-0945","PS":"Koramangala PS","Date":"2024-03-28 20:15","Crime":"Snatching / Robbery","Suspects":"Bunty @ Rakesh (Driver), Kallu @ Vikram (Pillion)","Vehicles":"KA-03-HX-4812","Zone":"South-East Zone"},
    {"Case ID":"FIR-2024-1102","PS":"Cyber Crime PS","Date":"2024-04-05 11:30","Crime":"Cyber Fraud","Suspects":"Manoj Kumar @ Rajat, Ramesh Shah","Vehicles":"None","Zone":"Cyber Cell"},
    {"Case ID":"FIR-2024-1240","PS":"Cyber Crime PS","Date":"2024-04-18 15:20","Crime":"Cyber Fraud","Suspects":"Manoj Kumar @ Rajat, Unknown Jamtara","Vehicles":"None","Zone":"Cyber Cell"},
    {"Case ID":"FIR-2024-1315","PS":"HSR Layout PS","Date":"2024-04-22 03:15","Crime":"House Burglary","Suspects":"Iron Rod Syndicate (3)","Vehicles":"White Swift Dzire","Zone":"South-East Zone"},
    {"Case ID":"FIR-2024-1420","PS":"Bellandur PS","Date":"2024-05-02 02:45","Crime":"House Burglary","Suspects":"Iron Rod Syndicate (3)","Vehicles":"White Swift Dzire","Zone":"East Zone"},
    {"Case ID":"FIR-2024-1508","PS":"Whitefield PS","Date":"2024-05-14 13:30","Crime":"Pretext Robbery","Suspects":"Pradeep @ Sonu","Vehicles":"Grey Honda Activa (mud-obscured)","Zone":"Whitefield Division"},
    {"Case ID":"FIR-2024-1622","PS":"Mahadevapura PS","Date":"2024-05-29 14:00","Crime":"Pretext Robbery","Suspects":"Pradeep @ Sonu","Vehicles":"KA-53-EJ-9014","Zone":"Whitefield Division"},
    {"Case ID":"FIR-2024-1750","PS":"Jayanagar PS","Date":"2024-06-10 20:30","Crime":"Snatching / Robbery","Suspects":"Bunty @ Rakesh, Kallu @ Vikram","Vehicles":"KA-03-HX-4812","Zone":"South Zone"},
    {"Case ID":"FIR-2024-1880","PS":"Electronic City PS","Date":"2024-06-25 03:30","Crime":"Automobile Theft","Suspects":"Mewat Car Theft Gang","Vehicles":"Hyundai Creta KA-51-MD-3301","Zone":"Electronic City Division"},
]

# ─────────────────────────────────────────────────────────────────────
# NETWORK GRAPH DATA (entity relationship)
# TODO: replace with fir_module.generate_network_graph_figure(G)
# ─────────────────────────────────────────────────────────────────────
NETWORK_NODES = [
    {"id":"CASE-2024-001","label":"CASE-2024-001","type":"Case","color":"#1D4ED8","size":28},
    {"id":"FIR-2024-0945","label":"FIR-2024-0945","type":"Case","color":"#3B82F6","size":20},
    {"id":"FIR-2024-0812","label":"FIR-2024-0812","type":"Case","color":"#3B82F6","size":20},
    {"id":"FIR-2024-1750","label":"FIR-2024-1750","type":"Case","color":"#3B82F6","size":20},
    {"id":"Bunty","label":"Bunty @ Rakesh","type":"Suspect","color":"#EF4444","size":22},
    {"id":"Kallu","label":"Kallu @ Vikram","type":"Suspect","color":"#EF4444","size":22},
    {"id":"KA-03-HX-4812","label":"KA-03-HX-4812","type":"Vehicle","color":"#F59E0B","size":18},
    {"id":"MO-Snatching","label":"Red Helmet Pillion Snatch","type":"MO_Signature","color":"#10B981","size":16},
]
NETWORK_EDGES = [
    ("CASE-2024-001","Bunty"),("CASE-2024-001","Kallu"),("CASE-2024-001","KA-03-HX-4812"),("CASE-2024-001","MO-Snatching"),
    ("FIR-2024-0945","Bunty"),("FIR-2024-0945","Kallu"),("FIR-2024-0945","KA-03-HX-4812"),
    ("FIR-2024-0812","Bunty"),("FIR-2024-0812","Kallu"),
    ("FIR-2024-1750","Bunty"),("FIR-2024-1750","KA-03-HX-4812"),
]

# ─────────────────────────────────────────────────────────────────────
# SAMPLE FIR SCENARIOS (sidebar dropdown)
# TODO: replace with SAMPLE_FIRS from fir_module.sample_firs
# ─────────────────────────────────────────────────────────────────────
SAMPLE_FIR_SCENARIOS = [
    "Sample 1: Bike-Borne Chain Snatching (Old Airport Road)",
    "Sample 2: BESCOM APK Phishing Fraud (Indiranagar)",
    "Sample 3: Midnight Villa Burglary (Sarjapur Road)",
    "Sample 4: Fake Courier Pretext Robbery (Whitefield)",
    "Sample 5: OBD Key-Clone Car Theft (Electronic City)",
]
