"""
Investigation Dossier and Action Summary Generator.
Synthesizes extracted intelligence, historical comparisons, repeat offender indicators,
and actionable investigation checklists for the Investigating Officer (IO).
"""

from typing import List, Dict, Any
from core.fir_backend.models import EntityExtraction, SimilarCaseResult, RepeatOffenderIndicator

LEGAL_DISCLAIMER = (
    "LEGAL NOTICE & HUMAN VERIFICATION MANDATE:\n"
    "This system is an automated Investigation Decision-Support Tool and DOES NOT declare guilt, "
    "establish legal culpability, or replace statutory criminal investigation procedures. "
    "All pattern matches, entity linkages, and repeat-offender indicators are automated hypotheses "
    "requiring independent verification, forensic confirmation, and evidentiary substantiation "
    "by the assigned Investigating Officer (IO) under the Code of Criminal Procedure (CrPC / BNSS)."
)


def generate_investigator_action_items(
    current_fir: EntityExtraction,
    top_matches: List[SimilarCaseResult],
    repeat_indicators: List[RepeatOffenderIndicator]
) -> List[Dict[str, str]]:
    """
    Generate prioritized, concrete operational action items for the police investigator.
    """
    actions = []

    # 1. Physical / Field Evidence Action
    if current_fir.vehicles_involved:
        veh_str = ", ".join(current_fir.vehicles_involved)
        actions.append({
            "category": "Surveillance & ANPR Alert",
            "priority": "HIGH",
            "task": f"Broadcast ANPR flash alert for vehicle(s) [{veh_str}] across all city toll gates, traffic junctions, and bordering check-posts.",
            "statutory_ref": "Section 91 CrPC (Summons to produce document or other thing)"
        })

    if current_fir.weapons and "None" not in current_fir.weapons[0]:
        weap_str = ", ".join(current_fir.weapons)
        actions.append({
            "category": "Forensic & Weapon Seizure",
            "priority": "HIGH",
            "task": f"Instruct Scene of Crime Officer (SOCO) to preserve tool-marks and fingerprints related to [{weap_str}]. Retrieve high-definition CCTV within 500m radius.",
            "statutory_ref": "Forensic Science Laboratory (FSL) Protocol"
        })

    # 2. Digital & Cyber Tracing
    if current_fir.phone_numbers:
        ph_str = ", ".join(current_fir.phone_numbers)
        actions.append({
            "category": "Telecommunication Requisition",
            "priority": "URGENT",
            "task": f"Issue immediate requisition to Telecom Service Provider for Call Detail Records (CDR), Subscriber Details (CAF), and Cell ID Tower Dump for [{ph_str}].",
            "statutory_ref": "Section 92 CrPC / Section 69 Information Technology Act"
        })

    # 3. Inter-Station Coordination (based on historical matches)
    if top_matches:
        top = top_matches[0]
        if top.similarity.overall_score >= 60.0:
            actions.append({
                "category": "Inter-Station IO Coordination",
                "priority": "MEDIUM",
                "task": f"Establish formal intelligence liaison with Station House Officer of {top.historical_case.police_station} regarding Case {top.historical_case.case_id} to compare custody status and interrogations.",
                "statutory_ref": "Inter-District Crime Intelligence Circular"
            })

    # 4. Suspect History-Sheet & Parole Verification
    if repeat_indicators:
        for ind in repeat_indicators:
            if ind.confidence_level == "HIGH":
                actions.append({
                    "category": "Repeat Offender Verification",
                    "priority": "CRITICAL",
                    "task": f"Check status of [{ind.suspect_or_cluster}]: verify current jail/bail status at Central Prison, interrogate known local associates, and conduct covert verification of known hideouts.",
                    "statutory_ref": "Habitual Offenders Act & Police Manual"
                })
                break

    # 5. Victim & Witness Support
    actions.append({
        "category": "Victim & Witness Identification",
        "priority": "STANDARD",
        "task": f"Schedule Test Identification Parade (TIP) before Executive Magistrate once suspects are apprehended. Ensure victim {current_fir.complainant} is provided safety and regular case updates.",
        "statutory_ref": "Section 54A CrPC (Identification of person arrested)"
    })

    return actions


def format_dossier_text(
    current_fir: EntityExtraction,
    top_matches: List[SimilarCaseResult],
    repeat_indicators: List[RepeatOffenderIndicator],
    action_items: List[Dict[str, str]]
) -> str:
    """
    Format complete Case Intelligence Dossier into a printable/exportable text report.
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"POLICE INTELLIGENCE & CRIME PATTERN DOSSIER")
    lines.append(f"CASE FILE: {current_fir.case_id} | PS: {current_fir.police_station}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(LEGAL_DISCLAIMER)
    lines.append("-" * 80)
    lines.append("")
    
    # Section 1
    lines.append("SECTION 1: INCIDENT SUMMARY & EXTRACTED ATTRIBUTES")
    lines.append(f"  • FIR Number / Case ID : {current_fir.case_id}")
    lines.append(f"  • Date & Time         : {current_fir.date_time}")
    lines.append(f"  • Primary Crime Type  : {current_fir.crime_type}")
    lines.append(f"  • Legal Sections      : {', '.join(current_fir.legal_sections)}")
    lines.append(f"  • Location & Zone     : {current_fir.location} ({current_fir.city_zone})")
    lines.append(f"  • Complainant / Victim : {current_fir.complainant}")
    lines.append(f"  • Named Suspects      : {', '.join(current_fir.accused_suspects) if current_fir.accused_suspects else 'Unidentified'}")
    lines.append(f"  • Vehicles Recorded   : {', '.join(current_fir.vehicles_involved) if current_fir.vehicles_involved else 'None'}")
    lines.append(f"  • Weapons / Tools     : {', '.join(current_fir.weapons) if current_fir.weapons else 'None'}")
    lines.append(f"  • Contact / Phone IDs : {', '.join(current_fir.phone_numbers) if current_fir.phone_numbers else 'None'}")
    lines.append(f"  • Stolen Property     : {', '.join(current_fir.stolen_property) if current_fir.stolen_property else 'None'}")
    lines.append("")
    
    # Section 2
    lines.append("SECTION 2: MODUS OPERANDI (MO) FINGERPRINT")
    lines.append(f"  • Full MO Narrative   : {current_fir.modus_operandi}")
    lines.append(f"  • Pretext / Approach  : {current_fir.mo_pretext_trick}")
    lines.append(f"  • Entry / Method      : {current_fir.mo_entry_exit}")
    lines.append(f"  • Transport Profile   : {current_fir.mo_transport}")
    lines.append(f"  • Timing Profile      : {current_fir.mo_timing_profile}")
    lines.append(f"  • Target Profile      : {current_fir.mo_target_profile}")
    lines.append("")

    # Section 3
    lines.append("SECTION 3: HISTORICAL CORRELATIONS & SIMILAR CASES")
    if top_matches:
        for i, match in enumerate(top_matches, 1):
            h = match.historical_case
            s = match.similarity
            lines.append(f"  [{i}] Case {h.case_id} ({h.police_station}) - Overall Match: {s.overall_score}%")
            lines.append(f"      - MO Overlap: {s.mo_similarity}% | Entity Overlap: {s.entity_overlap}% | Crime Type: {s.crime_type_match}%")
            lines.append(f"      - Matched Elements: {', '.join(s.matched_features) if s.matched_features else 'Typological alignment'}")
            lines.append(f"      - Investigator Note: {match.investigator_notes}")
            lines.append("")
    else:
        lines.append("  No significant historical matches detected above baseline threshold.")
        lines.append("")

    # Section 4
    lines.append("SECTION 4: REPEAT-OFFENDER INDICATORS & EVIDENCE REASONING")
    if repeat_indicators:
        for ind in repeat_indicators:
            lines.append(f"  [!] {ind.suspect_or_cluster} (CONFIDENCE: {ind.confidence_level} | RISK: {ind.risk_level})")
            lines.append(f"      Match Type : {ind.match_type}")
            lines.append(f"      Linked FIRs: {', '.join(ind.linked_case_ids)}")
            lines.append("      Evidence Reasoning:")
            for ev in ind.evidence_reasoning:
                lines.append(f"        - {ev}")
            lines.append(f"      Recommended Operational Action: {ind.recommended_action}")
            lines.append("")
    else:
        lines.append("  No repeat offender signatures identified for this specific pattern.")
        lines.append("")

    # Section 5
    lines.append("SECTION 5: OPERATIONAL ACTION ITEMS FOR INVESTIGATING OFFICER (IO)")
    for act in action_items:
        lines.append(f"  [{act['priority']}] {act['category']}")
        lines.append(f"      Task: {act['task']}")
        lines.append(f"      Authority / Ref: {act['statutory_ref']}")
        lines.append("")

    lines.append("=" * 80)
    lines.append("END OF INTELLIGENCE DOSSIER - FOR POLICE OFFICIAL USE ONLY")
    lines.append("=" * 80)

    return "\n".join(lines)
