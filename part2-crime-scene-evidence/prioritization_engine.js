/**
 * AI Crime Scene Evidence Prioritization Engine
 * Based on ISO/IEC 17025 Forensic Laboratory Triage & Legal Remand Standards.
 * Computes transparent, explainable priority scores (0-100) and maps specialized FSL examinations.
 */

// Forensic Test Mapping Table
const FORENSIC_TEST_CATALOG = {
  'Biological / DNA': {
    tests: [
      'Presumptive Kastle-Meyer & Confirmatory RSID-Blood Assay',
      'Automated Chelex/Magnetic Bead DNA Extraction & Quantifiler Trio',
      '24-Plex Autosomal STR Profiling + Y-STR Male Lineage Sequencing',
      'Differential Lysis for Mixed Epithelial / Touch DNA Separation'
    ],
    turnaroundUrgent: '12–24 Hours',
    turnaroundRoutine: '5–7 Days',
    specialPreservationAlert: '⚠️ CRITICAL BIO-HAZARD: Maintain strict cold chain (-20°C / 4°C). Store in breathable paper packaging to prevent mold/hydrolysis.'
  },
  'Digital / Cyber': {
    tests: [
      'Volatile RAM Capture & Live State Memory Preservation',
      'Write-Blocked Physical Bit-Stream Image Acquisition (EnCase / FTK)',
      'Hardware Chip-Off / ISP JTAG Physical Extraction & Decryption',
      'Cellebrite UFED Advanced Logical & File System Extraction',
      'Geofence, GPS Coordinates & Encrypted Messaging Decryption'
    ],
    turnaroundUrgent: '6–12 Hours (Battery / RAM volatile)',
    turnaroundRoutine: '3–5 Days',
    specialPreservationAlert: '⚠️ CRITICAL DIGITAL INTEGRITY: Keep isolated in Faraday RF Shielding bag. Connect external power pack to prevent power loss/kill switch activation.'
  },
  'Ballistics': {
    tests: [
      'Comparison Microscopy (Stereo 40x) for Striation & Toolmark Concordance',
      'Firing Pin Indentation, Breech Face & Ejector Mark 3D Topography',
      'IBIS (Integrated Ballistics Identification System) TraxHD Database Ingestion',
      'SEM-EDX (Scanning Electron Microscopy) for Gunshot Residue (GSR) Primer Analysis'
    ],
    turnaroundUrgent: '24–48 Hours',
    turnaroundRoutine: '7–10 Days',
    specialPreservationAlert: '⚠️ BALLISTIC INTEGRITY: Protect firing pin indent and extractor rim from metallic contact. Package in rigid padded container.'
  },
  'Latent Fingerprints': {
    tests: [
      'Cyanoacrylate Ester (Superglue) Vacuum Chamber Fuming',
      'Fluorescent Dye Staining (Rhodamine 6G / RAM) & Forensic Light Source (450nm)',
      'Automated Fingerprint Identification System (AFIS) 12-Minutiae Search',
      'Ninhydrin / DFO Chemical Fuming for Porous Substrates'
    ],
    turnaroundUrgent: '12–24 Hours',
    turnaroundRoutine: '3–4 Days',
    specialPreservationAlert: '⚠️ FRICTION RIDGE PRESERVATION: Avoid friction contact with surface. Protect from humidity degradation and direct sunlight.'
  },
  'Chemical / Explosives': {
    tests: [
      'Gas Chromatography-Mass Spectrometry (GC-MS) for High Explosive Residues',
      'High-Performance Liquid Chromatography (HPLC) for PETN/RDX Nitroaromatics',
      'FTIR (Fourier Transform Infrared Spectroscopy) for Oxidizer Identification',
      'Ion Chromatography (IC) for Inorganic Explosive Precursors'
    ],
    turnaroundUrgent: '12–18 Hours',
    turnaroundRoutine: '3–5 Days',
    specialPreservationAlert: '⚠️ HAZMAT / VOLATILE RESIDUE: Package in airtight inert nylon / metal containers to prevent volatile vapor evaporation.'
  },
  'Trace / Fiber': {
    tests: [
      'Polarized Light Microscopy (PLM) & Refractive Index Measurement',
      'Micro-FTIR Spectrometry for Polymer Classification',
      'Microspectrophotometry (MSP) for Dye Chromatographic Comparison',
      'Cross-Sectional Morphology & Scanning Electron Microscopy'
    ],
    turnaroundUrgent: '48 Hours',
    turnaroundRoutine: '5–8 Days',
    specialPreservationAlert: '⚠️ TRACE INTEGRITY: Seal in glassine envelopes to prevent static loss or ambient dust contamination.'
  },
  'Questioned Documents': {
    tests: [
      'Video Spectral Comparator (VSC 8000) for Infrared Luminescence / Char Reconstruction',
      'Electrostatic Detection Apparatus (ESDA) for Indented Handwriting Impressions',
      'High-Performance Thin Layer Chromatography (HPTLC) for Ink Composition',
      'Microscopic Line Cross & Sequence of Strokes Analysis'
    ],
    turnaroundUrgent: '24–48 Hours',
    turnaroundRoutine: '5–7 Days',
    specialPreservationAlert: '⚠️ FRAGILE DOCUMENT: Do not unfold or press charred remnants. Support in polyester batting boxes.'
  },
  'Physical / Toolmark': {
    tests: [
      'Comparative Toolmark Microscopy with Test Casts in Soft Lead / Clay',
      'Mikrosil Silicone Casting of Negative Tool Impressions',
      'Hardness & Metallurgical Trace Composition Analysis'
    ],
    turnaroundUrgent: '48 Hours',
    turnaroundRoutine: '7 Days',
    specialPreservationAlert: '⚠️ TOOLMARK CARE: Never insert suspect tool into questioned impression mark directly.'
  }
};

/**
 * Calculate multi-factor priority score (0-100) for an evidence item.
 */
function calculateEvidencePriority(evidence, crimeCase = {}) {
  const type = evidence.evidenceType || 'Physical / Toolmark';
  const degradationInput = (evidence.degradationRisk || 'MEDIUM').toUpperCase();
  const probativeInput = (evidence.probativeValue || 'HIGH').toUpperCase();
  const urgencyInput = (evidence.statutoryUrgency || 'MEDIUM').toUpperCase();

  // 1. Degradation & Perishability Score (0 - 35 points)
  let degradationScore = 15;
  let degradationNote = '';
  if (degradationInput === 'CRITICAL') {
    degradationScore = 35;
    degradationNote = 'Extreme risk of rapid degradation/power loss if not examined immediately.';
  } else if (degradationInput === 'HIGH') {
    degradationScore = 28;
    degradationNote = 'High perishability (biological decomposition / volatile residue evaporation).';
  } else if (degradationInput === 'MEDIUM') {
    degradationScore = 18;
    degradationNote = 'Moderate shelf stability under standard forensic packaging controls.';
  } else {
    degradationScore = 8;
    degradationNote = 'High physical stability; minimal degradation risk under ambient storage.';
  }

  // 2. Probative & Case Linkage Value (0 - 40 points)
  let probativeScore = 25;
  let probativeNote = '';
  if (probativeInput === 'CRITICAL') {
    probativeScore = 40;
    probativeNote = 'Direct physical nexus to core crime act, prime suspect, or primary weapon.';
  } else if (probativeInput === 'HIGH') {
    probativeScore = 32;
    probativeNote = 'Strong corroborative linkage connecting suspect identity, MO, or crime scene presence.';
  } else if (probativeInput === 'MEDIUM') {
    probativeScore = 20;
    probativeNote = 'Secondary contextual evidence corroborating sequence of events or timeline.';
  } else {
    probativeScore = 10;
    probativeNote = 'Circumstantial or ambient background trace; non-individualizing value.';
  }

  // 3. Statutory, Remand & Investigative Urgency (0 - 25 points)
  let urgencyScore = 12;
  let urgencyNote = '';
  if (urgencyInput === 'CRITICAL') {
    urgencyScore = 25;
    urgencyNote = 'Active fleeing suspect / statutory 24-hour arrest remand filing deadline.';
  } else if (urgencyInput === 'HIGH') {
    urgencyScore = 18;
    urgencyNote = 'Priority charge-sheet timeline / crucial lead for ongoing suspect interrogation.';
  } else if (urgencyInput === 'MEDIUM') {
    urgencyScore = 12;
    urgencyNote = 'Standard judicial investigation queue; trial preparation schedule.';
  } else {
    urgencyScore = 5;
    urgencyNote = 'Routine investigative archive; non-urgent judicial timeline.';
  }

  // Composite Score
  const totalScore = Math.min(100, Math.max(10, degradationScore + probativeScore + urgencyScore));

  // Determine Priority Tier
  let priorityLevel = 'MEDIUM';
  let badgeColor = 'info';
  let queueAction = 'Standard FSL Queue (Dispatch within 3–5 Days)';

  if (totalScore >= 85) {
    priorityLevel = 'CRITICAL';
    badgeColor = 'danger';
    queueAction = '🚨 IMMEDIATE LAB DISPATCH (Within 6–12 Hours)';
  } else if (totalScore >= 70) {
    priorityLevel = 'HIGH';
    badgeColor = 'warning';
    queueAction = '⚡ Priority Lab Queue (Dispatch within 24 Hours)';
  } else if (totalScore >= 50) {
    priorityLevel = 'MEDIUM';
    badgeColor = 'info';
    queueAction = '📦 Standard FSL Queue (Dispatch within 3–5 Days)';
  } else {
    priorityLevel = 'LOW';
    badgeColor = 'secondary';
    queueAction = '📁 Secondary Corroborative Archive';
  }

  // Fetch Recommended Forensic Tests & Lab Alerts
  const testInfo = FORENSIC_TEST_CATALOG[type] || FORENSIC_TEST_CATALOG['Physical / Toolmark'];

  // Generate Natural Language Forensic Reason
  const reason = `Priority classified as ${priorityLevel} (${totalScore}/100) based on ISO/IEC 17025 triage: ${probativeNote} ${degradationNote} ${urgencyNote}`;

  return {
    priorityLevel,
    priorityScore: totalScore,
    badgeColor,
    queueAction,
    scoreBreakdown: {
      degradationScore,
      degradationMax: 35,
      degradationNote,
      probativeScore,
      probativeMax: 40,
      probativeNote,
      urgencyScore,
      urgencyMax: 25,
      urgencyNote
    },
    reason,
    recommendedTests: testInfo.tests,
    estimatedTurnaround: priorityLevel === 'CRITICAL' ? testInfo.turnaroundUrgent : testInfo.turnaroundRoutine,
    preservationAlert: testInfo.specialPreservationAlert,
    requiresUrgentSpecializedTesting: priorityLevel === 'CRITICAL' || degradationInput === 'CRITICAL'
  };
}

/**
 * Generate a sorted FSL examination queue for all evidence items in a case.
 */
function buildFSLQueue(evidenceList, crimeCase = {}) {
  const analyzed = evidenceList.map(ev => {
    const analysis = calculateEvidencePriority(ev, crimeCase);
    return {
      ...ev,
      ...analysis
    };
  });

  // Sort descending by priority score
  analyzed.sort((a, b) => b.priorityScore - a.priorityScore);
  return analyzed;
}

module.exports = {
  calculateEvidencePriority,
  buildFSLQueue,
  FORENSIC_TEST_CATALOG
};
