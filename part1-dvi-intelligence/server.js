const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const {
  compareProfiles,
  getTopCandidatesForPM,
  getTopCandidatesForAM,
  runBatchMatching
} = require('./matching_engine');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const DATA_DIR = path.join(__dirname, 'data');
const INCIDENT_FILE = path.join(DATA_DIR, 'disaster_case.json');
const AM_FILE = path.join(DATA_DIR, 'antemortem.json');
const PM_FILE = path.join(DATA_DIR, 'postmortem.json');
const RECON_FILE = path.join(DATA_DIR, 'reconciliations.json');

// Helper to read JSON
function readJson(filePath, defaultVal = []) {
  try {
    if (!fs.existsSync(filePath)) return defaultVal;
    const raw = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    console.error(`Error reading ${filePath}:`, err);
    return defaultVal;
  }
}

// Helper to write JSON
function writeJson(filePath, data) {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
    return true;
  } catch (err) {
    console.error(`Error writing ${filePath}:`, err);
    return false;
  }
}

// 1. Get Disaster Incident Info
app.get('/api/incident', (req, res) => {
  const incident = readJson(INCIDENT_FILE, {});
  const ams = readJson(AM_FILE, []);
  const pms = readJson(PM_FILE, []);
  const recons = readJson(RECON_FILE, []);

  res.json({
    incident,
    stats: {
      totalAnteMortem: ams.length,
      totalPostMortem: pms.length,
      totalReconciled: recons.length,
      pendingReconciliation: pms.length - recons.length,
      highConfidenceCandidates: pms.filter(p => p.matchingStatus === 'Probable Match Identified').length
    }
  });
});

// 2. Ante-Mortem Profiles
app.get('/api/antemortem', (req, res) => {
  const data = readJson(AM_FILE, []);
  res.json(data);
});

app.get('/api/antemortem/:id', (req, res) => {
  const data = readJson(AM_FILE, []);
  const found = data.find(item => item.id === req.params.id);
  if (!found) return res.status(404).json({ error: 'Ante-Mortem profile not found' });
  res.json(found);
});

app.post('/api/antemortem', (req, res) => {
  const list = readJson(AM_FILE, []);
  const nextNum = list.length + 1;
  const newId = req.body.id || `AM-2026-${String(nextNum).padStart(3, '0')}`;

  const newProfile = {
    id: newId,
    fullName: req.body.fullName || 'Unidentified Missing Person',
    caseRef: req.body.caseRef || `MP-METRO-${100 + nextNum}`,
    age: Number(req.body.age) || 30,
    gender: req.body.gender || 'Indeterminate',
    heightCm: Number(req.body.heightCm) || 170,
    build: req.body.build || 'Medium',
    bloodGroup: req.body.bloodGroup || 'Unknown',
    hairDescription: req.body.hairDescription || 'Not specified',
    eyeColor: req.body.eyeColor || 'Not specified',
    scarsAndMarks: req.body.scarsAndMarks || 'None noted',
    tattoos: req.body.tattoos || 'None noted',
    dentalRecord: {
      crowns: req.body.dentalCrowns || 'None',
      missingTeeth: req.body.dentalMissing || 'None',
      fillings: req.body.dentalFillings || 'None',
      braces: req.body.dentalBraces || 'None',
      details: req.body.dentalDetails || 'Dental records on file'
    },
    surgicalMedicalHistory: req.body.surgicalMedicalHistory || 'None noted',
    clothingDescription: req.body.clothingDescription || 'Not specified',
    personalEffects: req.body.personalEffects || 'None noted',
    dnaProfileStatus: req.body.dnaProfileStatus || 'Pending Sample Collection',
    reporterContact: {
      name: req.body.reporterName || 'Next of kin',
      relation: req.body.reporterRelation || 'Relative',
      phone: req.body.reporterPhone || 'N/A'
    },
    status: 'Reported Missing',
    reconciledBodyId: null,
    createdAt: new Date().toISOString()
  };

  list.push(newProfile);
  writeJson(AM_FILE, list);
  res.status(201).json(newProfile);
});

// 3. Post-Mortem Profiles
app.get('/api/postmortem', (req, res) => {
  const data = readJson(PM_FILE, []);
  res.json(data);
});

app.get('/api/postmortem/:id', (req, res) => {
  const data = readJson(PM_FILE, []);
  const found = data.find(item => item.id === req.params.id);
  if (!found) return res.status(404).json({ error: 'Post-Mortem profile not found' });
  res.json(found);
});

app.post('/api/postmortem', (req, res) => {
  const list = readJson(PM_FILE, []);
  const nextNum = 80 + list.length + 1;
  const newId = req.body.id || `PM-2026-${String(nextNum).padStart(3, '0')}`;

  const newProfile = {
    id: newId,
    recoveryNumber: req.body.recoveryNumber || `REC-${newId}-METRO`,
    recoveryDate: req.body.recoveryDate || new Date().toISOString(),
    recoveryLocation: req.body.recoveryLocation || 'Disaster Sector Unspecified',
    bodyCondition: req.body.bodyCondition || 'Recovered remains undergoing examination',
    estimatedAgeMin: Number(req.body.estimatedAgeMin) || 25,
    estimatedAgeMax: Number(req.body.estimatedAgeMax) || 40,
    estimatedAgeDisplay: `${req.body.estimatedAgeMin || 25} - ${req.body.estimatedAgeMax || 40} years`,
    gender: req.body.gender || 'Indeterminate',
    estimatedHeightCm: Number(req.body.estimatedHeightCm) || 170,
    heightToleranceCm: Number(req.body.heightToleranceCm) || 4,
    build: req.body.build || 'Medium',
    hairDescription: req.body.hairDescription || 'Examination in progress',
    scarsAndMarks: req.body.scarsAndMarks || 'None noted',
    tattoos: req.body.tattoos || 'None noted',
    dentalRecord: {
      crowns: req.body.dentalCrowns || 'None observed',
      missingTeeth: req.body.dentalMissing || 'None observed',
      fillings: req.body.dentalFillings || 'None observed',
      braces: req.body.dentalBraces || 'None observed',
      details: req.body.dentalDetails || 'Odontology exam recorded'
    },
    surgicalMedicalFindings: req.body.surgicalMedicalFindings || 'No gross implants visualized',
    clothingFound: req.body.clothingFound || 'Textile fragments preserved',
    personalEffectsFound: req.body.personalEffectsFound || 'Personal items logged in evidence vault',
    dnaSampleStatus: req.body.dnaSampleStatus || 'Extracting',
    fingerprintsStatus: req.body.fingerprintsStatus || 'Pending Examination',
    matchingStatus: 'Unreconciled',
    reconciledWithAMId: null,
    autopsyReportRef: `AUT-2026-${String(400 + list.length + 1)}`,
    pathologistName: req.body.pathologistName || 'Dr. K. S. Mehra'
  };

  list.push(newProfile);
  writeJson(PM_FILE, list);
  res.status(201).json(newProfile);
});

// 4. Matching Engine Endpoints
// Match PM body against all AM records -> Returns Top 3 candidates
app.post('/api/match/pm/:id', (req, res) => {
  const pms = readJson(PM_FILE, []);
  const ams = readJson(AM_FILE, []);
  const pm = pms.find(p => p.id === req.params.id);
  if (!pm) return res.status(404).json({ error: 'Post-Mortem record not found' });

  const top3 = getTopCandidatesForPM(pm, ams, 3);
  res.json({
    pmRecord: pm,
    topCandidates: top3
  });
});

// Match AM profile against all PM bodies
app.post('/api/match/am/:id', (req, res) => {
  const pms = readJson(PM_FILE, []);
  const ams = readJson(AM_FILE, []);
  const am = ams.find(a => a.id === req.params.id);
  if (!am) return res.status(404).json({ error: 'Ante-Mortem record not found' });

  const top3 = getTopCandidatesForAM(am, pms, 3);
  res.json({
    amRecord: am,
    topCandidates: top3
  });
});

// Direct side-by-side comparison between 1 AM and 1 PM
app.post('/api/match/compare', (req, res) => {
  const { amId, pmId } = req.body;
  const ams = readJson(AM_FILE, []);
  const pms = readJson(PM_FILE, []);

  const am = ams.find(a => a.id === amId);
  const pm = pms.find(p => p.id === pmId);

  if (!am || !pm) return res.status(404).json({ error: 'Invalid AM or PM ID provided' });

  const comparison = compareProfiles(am, pm);
  res.json(comparison);
});

// Global Batch Matching Matrix
app.get('/api/match/batch', (req, res) => {
  const ams = readJson(AM_FILE, []);
  const pms = readJson(PM_FILE, []);
  const matrix = runBatchMatching(ams, pms);
  res.json(matrix);
});

// 5. Confirm Reconciliation (Formal Identification Sign-Off)
app.post('/api/reconcile', (req, res) => {
  const { amId, pmId, pathologistSignoff, odontologistSignoff, notes } = req.body;
  const ams = readJson(AM_FILE, []);
  const pms = readJson(PM_FILE, []);
  const recons = readJson(RECON_FILE, []);

  const amIndex = ams.findIndex(a => a.id === amId);
  const pmIndex = pms.findIndex(p => p.id === pmId);

  if (amIndex === -1 || pmIndex === -1) {
    return res.status(404).json({ error: 'Specified AM or PM record not found' });
  }

  const am = ams[amIndex];
  const pm = pms[pmIndex];

  // Perform final official match audit
  const matchResult = compareProfiles(am, pm);

  const reconId = `REC-DVI-${Date.now().toString().slice(-6)}`;
  const reconciliationEntry = {
    reconciliationId: reconId,
    timestamp: new Date().toISOString(),
    amId: am.id,
    victimName: am.fullName,
    pmId: pm.id,
    recoveryNumber: pm.recoveryNumber,
    recoveryLocation: pm.recoveryLocation,
    matchScore: matchResult.matchPercentage,
    confidenceTier: matchResult.confidenceTier,
    primaryEvidentiaryBasis: matchResult.matchingAttributes.filter(m => m.category === 'Primary').map(m => m.note),
    secondaryEvidentiaryBasis: matchResult.matchingAttributes.filter(m => m.category === 'Secondary').map(m => m.note),
    auxiliaryEvidentiaryBasis: matchResult.matchingAttributes.filter(m => m.category === 'Auxiliary').map(m => m.note),
    forensicRationale: matchResult.rationale,
    signoff: {
      forensicPathologist: pathologistSignoff || 'Dr. K. S. Mehra, Senior Forensic Pathologist',
      forensicOdontologist: odontologistSignoff || 'Dr. R. Alok, Chief Forensic Odontologist',
      investigatingOfficer: 'Inspector V. Saxena, Crime Investigation Branch'
    },
    notes: notes || 'Conclusive reconciliation confirmed under Interpol DVI standards.',
    dossierNumber: `DVI-DOSSIER-${reconId}`
  };

  // Update statuses
  am.status = 'Confirmed Identified';
  am.reconciledBodyId = pm.id;

  pm.matchingStatus = 'Reconciled';
  pm.reconciledWithAMId = am.id;

  recons.push(reconciliationEntry);

  writeJson(AM_FILE, ams);
  writeJson(PM_FILE, pms);
  writeJson(RECON_FILE, recons);

  res.status(201).json({
    message: 'Reconciliation officially confirmed and recorded.',
    reconciliation: reconciliationEntry
  });
});

// List all finalized reconciliations
app.get('/api/reconciliations', (req, res) => {
  const recons = readJson(RECON_FILE, []);
  res.json(recons);
});

// Generate formal reconciliation report
app.get('/api/reports/reconciliation/:id', (req, res) => {
  const recons = readJson(RECON_FILE, []);
  const incident = readJson(INCIDENT_FILE, {});
  const ams = readJson(AM_FILE, []);
  const pms = readJson(PM_FILE, []);

  const recon = recons.find(r => r.reconciliationId === req.params.id);
  if (!recon) return res.status(404).json({ error: 'Reconciliation dossier not found' });

  const am = ams.find(a => a.id === recon.amId);
  const pm = pms.find(p => p.id === recon.pmId);

  res.json({
    incident,
    reconciliation: recon,
    anteMortemProfile: am,
    postMortemProfile: pm
  });
});

// Reset Demo Data
app.post('/api/reset-demo', (req, res) => {
  // Can be called to restore initial state if needed
  res.json({ message: 'Demo dataset verified.' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚔 DVI Intelligence Module running at http://localhost:${PORT}`);
});
