"""
Data models for FIR Intelligence & Crime Pattern Detector.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EntityExtraction(BaseModel):
    case_id: str = Field(..., description="Unique FIR Identifier / Case No")
    police_station: str = Field(default="Unknown PS", description="Jurisdiction Police Station")
    date_time: str = Field(..., description="Date and time of incident occurrence")
    crime_type: str = Field(..., description="Categorized crime type")
    legal_sections: List[str] = Field(default_factory=list, description="IPC / BNS sections invoked")
    
    complainant: str = Field(default="Unknown", description="Complainant / Reporter name")
    victims: List[str] = Field(default_factory=list, description="Victim(s) name or identity")
    accused_suspects: List[str] = Field(default_factory=list, description="Accused / Suspect names, aliases, or descriptions")
    
    location: str = Field(..., description="Specific location / landmark of occurrence")
    city_zone: str = Field(default="General", description="City zone / district")
    
    # Modus Operandi (MO) Breakdown
    modus_operandi: str = Field(..., description="Full narrative summary of MO")
    mo_entry_exit: Optional[str] = Field(None, description="Entry/Exit method")
    mo_pretext_trick: Optional[str] = Field(None, description="Pretext, deceit or approach tactic")
    mo_transport: Optional[str] = Field(None, description="Vehicle / transport used by perpetrators")
    mo_timing_profile: Optional[str] = Field(None, description="Time window characteristic (e.g. Night, Rush Hour, Dawn)")
    mo_target_profile: Optional[str] = Field(None, description="Target victim profile (e.g. Lone woman, Senior citizen, Locked house)")
    
    # Tangible Entities
    weapons: List[str] = Field(default_factory=list, description="Weapons or tools reported")
    vehicles_involved: List[str] = Field(default_factory=list, description="Vehicle plate numbers or descriptions")
    stolen_property: List[str] = Field(default_factory=list, description="Items / valuables stolen or damaged")
    phone_numbers: List[str] = Field(default_factory=list, description="Phone numbers or digital identifiers mentioned")
    raw_text: str = Field(default="", description="Original raw FIR text")


class SimilarityBreakdown(BaseModel):
    overall_score: float = Field(..., description="Overall similarity score (0 - 100)")
    mo_similarity: float = Field(..., description="Modus Operandi semantic similarity (0 - 100)")
    crime_type_match: float = Field(..., description="Crime category correspondence (0 - 100)")
    location_proximity: float = Field(..., description="Geographic proximity score (0 - 100)")
    entity_overlap: float = Field(..., description="Direct entity overlap score (0 - 100)")
    matched_features: List[str] = Field(default_factory=list, description="Specific matching features")


class SimilarCaseResult(BaseModel):
    historical_case: EntityExtraction
    similarity: SimilarityBreakdown
    investigator_notes: str


class RepeatOffenderIndicator(BaseModel):
    suspect_or_cluster: str
    confidence_level: str  # "HIGH", "MODERATE", "LOW"
    match_type: str        # "Direct Identity", "Vehicle Match", "Digital Identifier", "Signature MO Match"
    evidence_reasoning: List[str]
    linked_case_ids: List[str]
    risk_level: str        # "High Pattern Recurrence", "Active Syndicate", "Emerging MO"
    recommended_action: str
