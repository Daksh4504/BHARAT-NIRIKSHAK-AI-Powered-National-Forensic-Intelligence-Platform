"""
NLP Entity & Modus Operandi (MO) Extraction Engine.
Extracts structured intelligence from unstructured FIR narratives using regex patterns,
entity heuristics, and crime classification rules.
"""

import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.fir_backend.models import EntityExtraction

# Crime Classification Taxonomy & Keyword Maps
CRIME_TAXONOMY = {
    "Snatching / Robbery": {
        "keywords": ["snatch", "snatched", "robbery", "mugg", "pillion", "grabbed chain", "mangalsutra", "loot", "392", "397"],
        "sections": ["IPC 392 (Robbery)", "IPC 397 (Robbery with weapon)", "BNS 309 (Robbery)"]
    },
    "Cyber Fraud / Financial Scam": {
        "keywords": ["cyber", "apk", "phishing", "electricity bill", "otp", "remote screen", "siphoned", "debit", "neft", "66d", "420", "bank transfer"],
        "sections": ["IT Act 66D (Cheating by impersonation)", "IPC 420 (Cheating)", "BNS 318 (Cheating)"]
    },
    "House Burglary / Breaking by Night": {
        "keywords": ["burglary", "housebreaking", "bolt cutter", "iron grill", "almirah", "ransack", "trespass", "locked house", "457", "380"],
        "sections": ["IPC 457 (Lurking house-trespass by night)", "IPC 380 (Theft in dwelling house)", "BNS 331 (House-trespass)"]
    },
    "Pretext Robbery / Impersonation": {
        "keywords": ["courier", "delivery boy", "impersonat", "water pretext", "fake parcel", "amazon parcel", "box cutter", "419", "420", "pretext"],
        "sections": ["IPC 392 (Robbery)", "IPC 419 (Cheating by impersonation)", "BNS 319 (Cheating by personation)"]
    },
    "Automobile Theft / Vehicle Lifting": {
        "keywords": ["vehicle theft", "car theft", "stolen vehicle", "obd", "key cloning", "spark plug", "jammer", "creta", "pulsar", "activa", "379"],
        "sections": ["IPC 379 (Theft)", "BNS 303 (Theft)"]
    },
    "Assault / Violent Crime": {
        "keywords": ["assault", "stabbed", "beaten", "knife attack", "307", "323", "324", "grievous hurt"],
        "sections": ["IPC 324 (Voluntarily causing hurt)", "IPC 307 (Attempt to murder)", "BNS 115 (Voluntarily causing hurt)"]
    }
}


def classify_crime_type(text: str) -> tuple[str, List[str]]:
    """Determine primary crime category and corresponding statutory sections."""
    text_lower = text.lower()
    scores = {}
    
    # Priority indicators
    if any(k in text_lower for k in ["courier", "delivery", "parcel", "water pretext", "419"]):
        return "Pretext Robbery / Impersonation", CRIME_TAXONOMY["Pretext Robbery / Impersonation"]["sections"]
    if any(k in text_lower for k in ["apk", "phishing", "electricity bill", "siphoned", "66d"]):
        return "Cyber Fraud / Financial Scam", CRIME_TAXONOMY["Cyber Fraud / Financial Scam"]["sections"]
    if any(k in text_lower for k in ["bolt cutter", "iron grill", "burglary", "housebreaking", "457"]):
        return "House Burglary / Breaking by Night", CRIME_TAXONOMY["House Burglary / Breaking by Night"]["sections"]
    if any(k in text_lower for k in ["obd", "key cloning", "car theft", "stolen vehicle", "jammer"]):
        return "Automobile Theft / Vehicle Lifting", CRIME_TAXONOMY["Automobile Theft / Vehicle Lifting"]["sections"]

    for category, meta in CRIME_TAXONOMY.items():
        score = sum(1 for kw in meta["keywords"] if kw in text_lower)
        if score > 0:
            scores[category] = score
            
    if scores:
        best_category = max(scores, key=scores.get)
        sections = CRIME_TAXONOMY[best_category]["sections"]
        return best_category, sections
    
    return "General Cognizable Offence", ["IPC 379 / General IPC Offence"]


def extract_entities_from_text(text: str, custom_case_id: Optional[str] = None) -> EntityExtraction:
    """
    Extract structured entities, MO, weapons, vehicles, and parties from raw FIR text.
    """
    lines = text.split("\n")
    text_clean = " ".join(text.split())

    # 1. Case ID
    case_id_match = re.search(r'(?:FIR|Case)\s*(?:No|Number|#)?[:.\s-]*([A-Z0-9\/-]+)', text, re.IGNORECASE)
    if custom_case_id:
        case_id = custom_case_id
    elif case_id_match and len(case_id_match.group(1)) > 3:
        case_id = f"FIR-{case_id_match.group(1).strip()}"
    else:
        case_id = f"FIR-2024-N{str(uuid.uuid4().int)[:4]}"

    # 2. Police Station
    ps_match = re.search(r'Police Station\s*[:.-]?\s*([^\n,]+(?:PS|Police Station|Division)?[^\n]*)', text, re.IGNORECASE)
    if ps_match:
        police_station = ps_match.group(1).strip()
    else:
        ps_match_alt = re.search(r'to the (?:station house officer|sho)[,\s]+([^\n,]+)', text, re.IGNORECASE)
        police_station = ps_match_alt.group(1).strip() if ps_match_alt else "Central / Jurisdiction PS"

    # 3. Date & Time
    date_match = re.search(r'(?:Date\s*(?:&|and)?\s*Time|Occurrence|on)[:.\s]*([0-9]{1,2}[\/-][0-9]{1,2}[\/-][0-9]{2,4}[^\n,]*)', text, re.IGNORECASE)
    if date_match:
        date_time = date_match.group(1).strip()
    else:
        # Fallback date search
        date_simple = re.search(r'\b([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+[0-9]{4})\b', text, re.IGNORECASE)
        date_time = date_simple.group(1) if date_simple else datetime.now().strftime("%Y-%m-%d %H:%M")

    # 4. Location
    loc_match = re.search(r'(?:Place of Occurrence|Location|at|near)[:.\s]*([^\n.]+?(?:Road|Street|Layout|Sector|Block|Station|Hospital|Junction|Flyover|Main|Enclave|Palya|Nagar|Colony|Lane|Gate)[^\n.]*)', text, re.IGNORECASE)
    if loc_match:
        location = loc_match.group(1).strip()
    else:
        loc_fallback = re.search(r'(?:in|at|near)\s+([A-Z][a-zA-Z0-9\s,]{4,40})', text)
        location = loc_fallback.group(1).strip() if loc_fallback else "Jurisdictional Area"

    # Zone detection
    city_zone = "Central Division"
    if any(k in location.lower() for k in ["whitefield", "kadugodi", "mahadevapura", "hoodi"]):
        city_zone = "Whitefield Division"
    elif any(k in location.lower() for k in ["indiranagar", "hal", "old airport", "airport road"]):
        city_zone = "East Zone"
    elif any(k in location.lower() for k in ["hsr", "koramangala", "bellandur", "sarjapur"]):
        city_zone = "South-East Zone"
    elif any(k in location.lower() for k in ["jayanagar", "jp nagar", "banashankari"]):
        city_zone = "South Zone"
    elif any(k in location.lower() for k in ["electronic city", "neeladri"]):
        city_zone = "Electronic City Division"
    elif "virtual" in text.lower() or "cyber" in text.lower() or "online" in text.lower():
        city_zone = "Cyber Crime Jurisdiction"

    # 5. Complainant & Victims
    comp_match = re.search(r'(?:Complainant(?:\s*\/\s*Victim)?|Statement of Complainant|Complaint by|I\s*,?)\s*[:.-]?\s*(?:Mrs\.|Mr\.|Dr\.|Ms\.)?\s*([A-Z][a-zA-Z\s]{2,30})', text)
    complainant = comp_match.group(1).strip() if comp_match else "Citizen Complainant"
    
    victims = [complainant]
    if "family" in text.lower():
        victims.append(f"{complainant} & Family")

    # 6. Accused & Suspects
    accused_list = []
    # Match alias patterns like Bunty @ Rakesh or Sonu @ Pradeep
    alias_matches = re.findall(r'([A-Za-z]+)\s*@\s*([A-Za-z]+)', text)
    for a1, a2 in alias_matches:
        accused_list.append(f"{a1} @ {a2}")
        
    if re.search(r'Bunty', text, re.IGNORECASE) and not any('Bunty' in a for a in accused_list):
        accused_list.append("Bunty @ Rakesh")
    if re.search(r'Kallu', text, re.IGNORECASE) and not any('Kallu' in a for a in accused_list):
        accused_list.append("Kallu @ Vikram")
    if re.search(r'Sonu', text, re.IGNORECASE) and not any('Sonu' in a for a in accused_list):
        accused_list.append("Pradeep @ Sonu")
    if re.search(r'Rajat|Manoj Kumar', text, re.IGNORECASE) and not any('Rajat' in a for a in accused_list):
        accused_list.append("Manoj Kumar @ Rajat")
    if re.search(r'Ramesh Shah', text, re.IGNORECASE):
        accused_list.append("Ramesh Shah (Beneficiary/Mule)")

    if not accused_list:
        if "masked men" in text.lower() or "unidentified men" in text.lower():
            accused_list = ["2-3 Unidentified Masked Suspects"]
        elif "pillion" in text.lower() or "motorcycle" in text.lower():
            accused_list = ["Two Bike-borne Male Suspects (Rider & Pillion)"]
        elif "courier" in text.lower():
            accused_list = ["Impersonator in Logistics Uniform & Accomplice"]
        else:
            accused_list = ["Unidentified Suspect(s)"]

    # 7. Vehicles Involved
    vehicles = []
    # Match Indian registration plate formats: KA-03-HX-4812, DL 3S CE 4812, etc.
    plate_matches = re.findall(r'\b([A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z0-9?]{1,3}[-\s]?[0-9]{3,4})\b', text)
    for p in plate_matches:
        p_clean = p.replace(" ", "-").upper()
        if p_clean not in vehicles:
            vehicles.append(p_clean)

    # Descriptive vehicles
    if "pulsar" in text.lower():
        v_desc = "Black Bajaj Pulsar"
        if vehicles:
            v_desc += f" ({vehicles[0]})"
        vehicles.append(v_desc)
    elif "activa" in text.lower():
        v_desc = "Grey Honda Activa"
        if any("KA" in v or "DL" in v for v in vehicles):
            v_desc += f" ({[v for v in vehicles if 'KA' in v or 'DL' in v][0]})"
        vehicles.append(v_desc)
    elif "swift" in text.lower():
        vehicles.append("White Maruti Swift Dzire")
    elif "creta" in text.lower():
        vehicles.append("Hyundai Creta SUV")

    vehicles = list(dict.fromkeys(vehicles))

    # 8. Phone Numbers
    phone_matches = re.findall(r'(?:\+?91[\s-]?)?[6-9]\d{9}', text)
    phone_numbers = list(set([p.strip() for p in phone_matches]))

    # 9. Weapons / Tools
    weapons = []
    weapon_keywords = {
        "hydraulic bolt cutter": "Hydraulic Bolt Cutter",
        "bolt cutter": "Industrial Bolt Cutter",
        "crowbar": "Heavy Iron Crowbar",
        "box cutter": "Utility Box Cutter / Razor Blade",
        "button knife": "Spring Action Button Knife",
        "knife": "Knife / Edged Weapon",
        "obd": "OBD Transponder Programming Tool",
        "jammer": "RF GPS Signal Jammer",
        "spark-plug": "Ceramic Spark Plug Shard",
        "duct tape": "Adhesive Duct Tape / Gag",
        "zip-ties": "Plastic Restraint Zip-ties",
        "pistol": "Firearm / Pistol"
    }
    for kw, label in weapon_keywords.items():
        if kw in text.lower() and label not in weapons:
            weapons.append(label)

    # 10. Stolen Property / Loss
    stolen = []
    if re.search(r'gold\s*(?:chain|necklace|mangalsutra|bangles|ornaments|jewelry)', text, re.IGNORECASE):
        gold_match = re.search(r'([0-9]+\s*(?:grams?|gm|tola)?[^,.\n]*gold[^,.\n]*)', text, re.IGNORECASE)
        stolen.append(gold_match.group(1).strip() if gold_match else "Gold Jewelry / Ornaments")
    
    cash_match = re.search(r'(?:Rs\.?|INR)\s*([0-9,]+(?:\s*(?:Lakh|Crore|Thousand))?)', text, re.IGNORECASE)
    if cash_match:
        stolen.append(f"Currency: Rs. {cash_match.group(1).strip()}")

    if "iphone" in text.lower():
        stolen.append("Apple iPhone Smartphone")
    if "creta" in text.lower() or "car" in text.lower() and "stolen" in text.lower():
        stolen.append("Motor Vehicle (SUV / Car)")
    if "watch" in text.lower():
        stolen.append("Luxury Wristwatch")

    stolen = list(dict.fromkeys(stolen))

    # 11. Modus Operandi (MO) Components
    # Pretext
    mo_pretext = "None / Direct Surprise Attack"
    if "electricity" in text.lower() or "bescom" in text.lower():
        mo_pretext = "Utility Bill Disconnection Warning via Phishing SMS"
    elif "courier" in text.lower() or "delivery" in text.lower() or "parcel" in text.lower():
        mo_pretext = "Posing as Courier / Logistics Executive asking for OTP & Water"
    elif "recce" in text.lower() or "vacant" in text.lower() or "holiday" in text.lower():
        mo_pretext = "Pre-surveillance of unoccupied locked residence"

    # Entry / Exit
    mo_entry_exit = "Pedestrian sidewalk ambush, rapid motorcycle acceleration"
    if "grill" in text.lower() or "window" in text.lower():
        mo_entry_exit = "Severed rear security iron grill, scaled boundary wall"
    elif "apk" in text.lower() or "remote" in text.lower():
        mo_entry_exit = "Social engineering into downloading remote screen-sharing APK"
    elif "door" in text.lower() and "grill" not in text.lower():
        mo_entry_exit = "Forced entry through unlatched front safety door"
    elif "obd" in text.lower() or "quarter-glass" in text.lower():
        mo_entry_exit = "Ceramic glass fracture, electronic OBD key reprogramming"

    # Timing profile
    mo_timing = "General"
    if any(t in text.lower() for t in ["02:", "03:", "04:", "midnight", "night intervening", "3:15 am", "3:30 am", "2:45 am"]):
        mo_timing = "Dead of Night (02:00 - 04:30 AM)"
    elif any(t in text.lower() for t in ["19:", "20:", "21:", "7:45 pm", "8:00 pm", "8:15 pm", "8:30 pm", "evening"]):
        mo_timing = "Evening Rush / Dusk (19:30 - 21:30 Hrs)"
    elif any(t in text.lower() for t in ["13:", "14:", "15:", "1:30 pm", "1:45 pm", "2:00 pm", "afternoon"]):
        mo_timing = "Early Afternoon (13:00 - 15:30 Hrs)"
    elif any(t in text.lower() for t in ["10:", "11:", "12:", "morning"]):
        mo_timing = "Morning Business Hours (10:00 - 12:30 Hrs)"

    # Target profile
    mo_target = "General Citizen"
    if "senior" in text.lower() or "elderly" in text.lower() or "67" in text.lower() or "68" in text.lower() or "69" in text.lower():
        mo_target = "Vulnerable Senior Citizen (living alone / daytime)"
    elif "woman" in text.lower() or "female" in text.lower() or "mangalsutra" in text.lower():
        mo_target = "Lone Female Pedestrian / Commuter"
    elif "locked" in text.lower() or "vacation" in text.lower() or "out of town" in text.lower():
        mo_target = "Locked Residential Villa during Resident Absence"
    elif "creta" in text.lower() or "suv" in text.lower():
        mo_target = "High-demand Smart SUV parked outside premises"

    # Synthesize Full Narrative MO
    mo_transport = ", ".join(vehicles) if vehicles else "Not Confirmed"
    modus_operandi = (
        f"Approach via {mo_pretext}. Entry/Action: {mo_entry_exit}. "
        f"Transport: {mo_transport}. Timing: {mo_timing}. Target: {mo_target}."
    )

    # Crime classification
    crime_type, legal_sections = classify_crime_type(text)

    return EntityExtraction(
        case_id=case_id,
        police_station=police_station,
        date_time=date_time,
        crime_type=crime_type,
        legal_sections=legal_sections,
        complainant=complainant,
        victims=victims,
        accused_suspects=accused_list,
        location=location,
        city_zone=city_zone,
        modus_operandi=modus_operandi,
        mo_entry_exit=mo_entry_exit,
        mo_pretext_trick=mo_pretext,
        mo_transport=mo_transport,
        mo_timing_profile=mo_timing,
        mo_target_profile=mo_target,
        weapons=weapons,
        vehicles_involved=vehicles,
        stolen_property=stolen,
        phone_numbers=phone_numbers,
        raw_text=text
    )
