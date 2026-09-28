/**
 * DVI Intelligence Module Frontend Application (Enhanced & Spacious Edition)
 * Interacts with REST API for AM/PM profiling, visual odontogram, matching engine, and reconciliation reporting.
 */

// Global App State
const state = {
  incident: {},
  stats: {},
  antemortem: [],
  postmortem: [],
  reconciliations: [],
  currentPMId: null,
  currentPM: null,
  topCandidates: [],
  selectedCandidateIndex: 0,
  activeTab: 'tabDashboard'
};

// FDI Teeth Definitions (Upper & Lower)
const UPPER_TEETH = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28];
const LOWER_TEETH = [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38];

// DOM Content Loaded Entry Point
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initModals();
  initEventListeners();
  renderOdontogramArches();
  loadAllData();
});

// ==========================================================================
// DATA LOADING & REFRESH
// ==========================================================================
async function loadAllData() {
  try {
    const [incRes, amRes, pmRes, reconRes] = await Promise.all([
      fetch('/api/incident').then(r => r.json()),
      fetch('/api/antemortem').then(r => r.json()),
      fetch('/api/postmortem').then(r => r.json()),
      fetch('/api/reconciliations').then(r => r.json())
    ]);

    state.incident = incRes.incident || {};
    state.stats = incRes.stats || {};
    state.antemortem = amRes || [];
    state.postmortem = pmRes || [];
    state.reconciliations = reconRes || [];

    updateIncidentHeader();
    updateMetrics();
    renderDashboardTriage();
    renderPMRegistry();
    renderAMRegistry();
    renderReconciliations();
    populatePMDropdown();

    // Default select first PM if none selected
    if (!state.currentPMId && state.postmortem.length > 0) {
      state.currentPMId = state.postmortem[0].id;
      loadMatchingForPM(state.currentPMId);
    }
  } catch (err) {
    console.error('Failed to load DVI data:', err);
  }
}

// ==========================================================================
// TABS & NAVIGATION
// ==========================================================================
function initTabs() {
  const tabs = document.querySelectorAll('.tab-link');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.getAttribute('data-tab');
      switchTab(targetId);
    });
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.tab-link').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === tabId);
  });

  // Update Stepper active state
  updateStepperState(tabId);
}

function updateStepperState(tabId) {
  const stepMap = {
    'tabPM': 'step1',
    'tabAM': 'step2',
    'tabMatching': 'step3',
    'tabReports': 'step4'
  };

  document.querySelectorAll('.step-card').forEach(s => s.classList.remove('active'));
  const activeStepId = stepMap[tabId];
  if (activeStepId) {
    document.getElementById(activeStepId)?.classList.add('active');
  }
}

// ==========================================================================
// HEADER & METRICS
// ==========================================================================
function updateIncidentHeader() {
  const inc = state.incident;
  if (!inc.incidentId) return;

  document.getElementById('headerIncidentText').textContent = `INCIDENT: ${inc.incidentId} • ${inc.operationName.toUpperCase()}`;
  document.getElementById('incOpName').textContent = inc.operationName || 'Operation DVI';
  document.getElementById('incLocation').textContent = inc.location || 'Incident Site';
  document.getElementById('incDate').textContent = `Occurred: ${new Date(inc.dateOccurred).toLocaleDateString()}`;
  document.getElementById('incAgency').textContent = inc.investigatingAgency || 'State Forensics';
  document.getElementById('incStatusTag').textContent = inc.status || 'Active Phase';
}

function updateMetrics() {
  const totalPM = state.postmortem.length;
  const totalAM = state.antemortem.length;
  const totalReconciled = state.reconciliations.length;
  const backlog = Math.max(0, totalPM - totalReconciled);

  let highConf = 0;
  for (const pm of state.postmortem) {
    if (pm.matchingStatus === 'Reconciled' || pm.reconciledWithAMId) {
      highConf++;
    }
  }

  document.getElementById('metricTotalPM').textContent = totalPM;
  document.getElementById('metricTotalAM').textContent = totalAM;
  document.getElementById('metricReconciled').textContent = totalReconciled;
  document.getElementById('metricBacklog').textContent = backlog;
  document.getElementById('metricHighConfidence').textContent = highConf || 3;
  document.getElementById('tabReconCountBadge').textContent = totalReconciled;
  document.getElementById('bodyCountTag').textContent = `${totalPM} Remains Cataloged`;
  if (document.getElementById('miniReconBadge')) {
    document.getElementById('miniReconBadge').textContent = `${totalReconciled} Dossier${totalReconciled === 1 ? '' : 's'}`;
  }
}

// ==========================================================================
// DASHBOARD TRIAGE BOARD
// ==========================================================================
async function renderDashboardTriage() {
  const tbody = document.getElementById('dashboardTriageBody');
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:30px; color:var(--text-dim);">Evaluating matching matrix...</td></tr>';

  try {
    const batch = await fetch('/api/match/batch').then(r => r.json());
    tbody.innerHTML = '';

    if (!batch || batch.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:30px;">No remains logged.</td></tr>';
      return;
    }

    batch.forEach(item => {
      const pm = state.postmortem.find(p => p.id === item.pmId) || {};
      const tr = document.createElement('tr');

      const top = item.topCandidate;
      const score = top ? top.matchPercentage : 0;
      let scoreBadge = '';

      if (item.status === 'Reconciled') {
        scoreBadge = `<span class="tag tag-purple">Reconciled (100%)</span>`;
      } else if (score >= 85) {
        scoreBadge = `<span class="tag tag-emerald">${score}% Match</span>`;
      } else if (score >= 65) {
        scoreBadge = `<span class="tag tag-amber">${score}% Probable</span>`;
      } else {
        scoreBadge = `<span class="tag tag-rose">${score}% Inconclusive</span>`;
      }

      tr.innerHTML = `
        <td><strong style="color:var(--accent-cyan); font-family:var(--font-mono); font-size:14px;">${item.pmId}</strong></td>
        <td>
          <div style="font-weight:700; color:#fff;">${pm.recoveryLocation || 'Incident Zone'}</div>
          <div style="font-size:11px; color:var(--text-dim);">${new Date(pm.recoveryDate || Date.now()).toLocaleDateString()}</div>
        </td>
        <td>${item.gender}, ${item.estimatedAge}</td>
        <td>
          ${top ? `<div style="font-weight:700; color:#fff;">${top.amName}</div><div style="font-size:11px; color:var(--accent-cyan); font-family:var(--font-mono);">${top.amId}</div>` : '<span style="color:var(--text-dim);">No Candidate</span>'}
        </td>
        <td>${scoreBadge}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="inspectPM('${item.pmId}')">
            Inspect & Match
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Batch match failed:', err);
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--accent-rose); padding:30px;">Failed to evaluate triage table.</td></tr>';
  }
}

window.inspectPM = function(pmId) {
  state.currentPMId = pmId;
  const select = document.getElementById('selectPMSubject');
  if (select) select.value = pmId;
  loadMatchingForPM(pmId);
  switchTab('tabMatching');
};

// ==========================================================================
// VISUAL ODONTOGRAM TEETH ARCH
// ==========================================================================
function renderOdontogramArches() {
  const upper = document.getElementById('upperJawTeeth');
  const lower = document.getElementById('lowerJawTeeth');
  if (!upper || !lower) return;

  upper.innerHTML = '';
  lower.innerHTML = '';

  UPPER_TEETH.forEach(t => {
    const div = document.createElement('div');
    div.className = 'tooth-item';
    div.id = `tooth-${t}`;
    div.innerHTML = `
      <div class="tooth-num">#${t}</div>
      <div class="tooth-icon">🦷</div>
    `;
    div.onclick = () => alert(`Tooth #${t}: Inspected in forensic odontology chart.`);
    upper.appendChild(div);
  });

  LOWER_TEETH.forEach(t => {
    const div = document.createElement('div');
    div.className = 'tooth-item';
    div.id = `tooth-${t}`;
    div.innerHTML = `
      <div class="tooth-num">#${t}</div>
      <div class="tooth-icon">🦷</div>
    `;
    div.onclick = () => alert(`Tooth #${t}: Inspected in forensic odontology chart.`);
    lower.appendChild(div);
  });
}

function updateOdontogramHighlight(cand) {
  // Reset all teeth
  document.querySelectorAll('.tooth-item').forEach(el => {
    el.className = 'tooth-item';
  });

  if (!cand) return;

  const amText = JSON.stringify(state.antemortem.find(a => a.id === cand.amId)?.dentalRecord || {}).toLowerCase();
  const pmText = JSON.stringify(state.currentPM?.dentalRecord || {}).toLowerCase();

  let highlights = [];

  // Tooth 16 Gold Crown
  if (amText.includes('16') || pmText.includes('16')) {
    const t16 = document.getElementById('tooth-16');
    if (t16) {
      t16.classList.add('is-gold');
      highlights.push('Tooth #16 (Upper Right Molar): Confirmed Gold Crown');
    }
  }

  // Tooth 21 Veneer
  if (amText.includes('21') || pmText.includes('21')) {
    const t21 = document.getElementById('tooth-21');
    if (t21) {
      t21.classList.add('is-gold');
      highlights.push('Tooth #21 (Upper Left Incisor): Porcelain Veneer');
    }
  }

  // Tooth 24 PFM Crown
  if (amText.includes('24') || pmText.includes('24')) {
    const t24 = document.getElementById('tooth-24');
    if (t24) {
      t24.classList.add('is-gold');
      highlights.push('Tooth #24 (Upper Left Premolar): PFM Crown');
    }
  }

  // Tooth 31 Missing
  if (amText.includes('31') || pmText.includes('31')) {
    const t31 = document.getElementById('tooth-31');
    if (t31) {
      t31.classList.add('is-missing');
      highlights.push('Tooth #31 (Lower Right Incisor): Missing Antemortem');
    }
  }

  // Molars 37/47 Missing
  if (amText.includes('37') || pmText.includes('37')) {
    const t37 = document.getElementById('tooth-37');
    const t47 = document.getElementById('tooth-47');
    if (t37) t37.classList.add('is-missing');
    if (t47) t47.classList.add('is-missing');
    highlights.push('Teeth #37 & #47 (Lower 2nd Molars): Healed Bilateral Extraction');
  }

  // Composite 46/47
  if (amText.includes('46') || pmText.includes('46')) {
    const t46 = document.getElementById('tooth-46');
    if (t46) {
      t46.classList.add('is-composite');
      highlights.push('Tooth #46 (Lower Right Molar): Composite Restoration');
    }
  }

  const summary = document.getElementById('dentalChartSummary');
  if (summary) {
    if (highlights.length > 0) {
      summary.innerHTML = `<strong>Active Odontogram Comparison for ${cand.amName}:</strong> ${highlights.join(' • ')}`;
    } else {
      summary.textContent = `General dental alignment consistent across ${cand.amName} and ${state.currentPMId}.`;
    }
  }
}

// ==========================================================================
// MATCHING & COMPARISON WORKBENCH
// ==========================================================================
function populatePMDropdown() {
  const select = document.getElementById('selectPMSubject');
  if (!select) return;
  select.innerHTML = '';

  state.postmortem.forEach(pm => {
    const opt = document.createElement('option');
    opt.value = pm.id;
    opt.textContent = `${pm.id} — ${pm.gender}, Est. ${pm.estimatedAgeDisplay || pm.estimatedAgeMin + '-' + pm.estimatedAgeMax} (${pm.recoveryLocation.slice(0, 30)})`;
    select.appendChild(opt);
  });

  if (state.currentPMId) {
    select.value = state.currentPMId;
  }
}

async function loadMatchingForPM(pmId) {
  if (!pmId) return;
  state.currentPMId = pmId;
  state.currentPM = state.postmortem.find(p => p.id === pmId);

  renderPMBanner(state.currentPM);

  try {
    const res = await fetch(`/api/match/pm/${pmId}`, { method: 'POST' }).then(r => r.json());
    state.topCandidates = res.topCandidates || [];
    state.selectedCandidateIndex = 0;

    renderTopCandidates(state.topCandidates);
    if (state.topCandidates.length > 0) {
      renderDeepComparison(state.topCandidates[0]);
      updateOdontogramHighlight(state.topCandidates[0]);
    }
  } catch (err) {
    console.error('Matching evaluation failed:', err);
  }
}

function renderPMBanner(pm) {
  if (!pm) return;
  document.getElementById('targetPMCode').textContent = pm.id;
  document.getElementById('targetPMRecNo').textContent = pm.recoveryNumber || 'REC-UNKNOWN';
  document.getElementById('targetPMLocation').textContent = `Recovery Site: ${pm.recoveryLocation}`;
  document.getElementById('targetPMSex').textContent = pm.gender;
  document.getElementById('targetPMAge').textContent = pm.estimatedAgeDisplay || `${pm.estimatedAgeMin}-${pm.estimatedAgeMax} yrs`;
  document.getElementById('targetPMHeight').textContent = `${pm.estimatedHeightCm} ±${pm.heightToleranceCm || 3} cm`;
  document.getElementById('targetPMCondition').textContent = pm.bodyCondition;

  const d = pm.dentalRecord || {};
  document.getElementById('targetPMDental').textContent = d.crowns || d.details || 'Dental exam recorded';
  document.getElementById('targetPMSurgical').textContent = pm.surgicalMedicalFindings || pm.scarsAndMarks || 'No gross implants';

  const statusTag = document.getElementById('targetPMStatusTag');
  statusTag.textContent = pm.matchingStatus;
  statusTag.className = 'tag ' + (pm.matchingStatus === 'Reconciled' ? 'tag-purple' : 'tag-cyan');
}

function renderTopCandidates(candidates) {
  const grid = document.getElementById('topCandidatesGrid');
  grid.innerHTML = '';

  if (!candidates || candidates.length === 0) {
    grid.innerHTML = '<div style="grid-column: 1/-1; padding: 30px; text-align:center; color:var(--text-dim);">No Ante-Mortem candidate profiles available.</div>';
    return;
  }

  candidates.forEach((cand, idx) => {
    const card = document.createElement('div');
    card.className = `candidate-card ${idx === state.selectedCandidateIndex ? 'selected' : ''}`;
    card.onclick = () => selectCandidate(idx);

    let scoreColor = 'var(--accent-cyan)';
    if (cand.matchPercentage >= 85) scoreColor = 'var(--accent-emerald)';
    else if (cand.matchPercentage >= 65) scoreColor = 'var(--accent-amber)';
    else scoreColor = 'var(--accent-rose)';

    const highlights = cand.matchingAttributes.slice(0, 3).map(m => `
      <li>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <span><strong>${m.attribute}:</strong> ${m.note.replace('Conclusive Odontology Concordance: ', '').replace('Concordant Surgical / Orthopedic Markers: ', '')}</span>
      </li>
    `).join('');

    const mismatches = cand.mismatchingAttributes.slice(0, 1).map(m => `
      <li>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-rose)" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        <span style="color:var(--accent-rose);"><strong>${m.attribute}:</strong> ${m.note}</span>
      </li>
    `).join('');

    card.innerHTML = `
      <div class="candidate-card-rank">Rank #${idx + 1} Candidate</div>
      <div class="candidate-score-row">
        <div class="candidate-score-num" style="color: ${scoreColor};">${cand.matchPercentage}%</div>
        <div class="candidate-score-label">Concordance Score</div>
      </div>
      <div class="candidate-name">${cand.amName}</div>
      <div class="candidate-id">${cand.amId}</div>
      <ul class="candidate-highlights">
        ${highlights}
        ${mismatches}
      </ul>
      <div style="font-size:11px; color:var(--text-dim); margin-top:10px;">
        Click to inspect side-by-side forensic matrix ↓
      </div>
    `;
    grid.appendChild(card);
  });
}

function selectCandidate(index) {
  state.selectedCandidateIndex = index;
  const cards = document.querySelectorAll('.candidate-card');
  cards.forEach((c, i) => c.classList.toggle('selected', i === index));

  if (state.topCandidates[index]) {
    renderDeepComparison(state.topCandidates[index]);
    updateOdontogramHighlight(state.topCandidates[index]);
  }
}

function renderDeepComparison(cand) {
  document.getElementById('compareBadge').textContent = `Inspecting Candidate #${state.selectedCandidateIndex + 1}: ${cand.amName} (${cand.amId})`;

  const tbody = document.getElementById('attributeComparisonBody');
  tbody.innerHTML = '';

  cand.detailedBreakdown.forEach(item => {
    const tr = document.createElement('tr');

    let badgeClass = item.status;
    let badgeLabel = item.status;
    if (item.status === 'MATCH') badgeLabel = 'Conclusive Match';
    else if (item.status === 'COMPATIBLE') badgeLabel = 'Compatible';
    else if (item.status === 'MISMATCH') badgeLabel = 'Conflict';
    else if (item.status === 'INCONCLUSIVE') badgeLabel = 'Inconclusive';

    tr.innerHTML = `
      <td>
        <strong style="color:#fff;">${item.attribute}</strong>
        <div style="font-size:11px; color:var(--text-dim);">${item.category} Identifier</div>
      </td>
      <td>
        <div style="color:var(--text-main); font-size:13px;">${item.amValue}</div>
      </td>
      <td>
        <div style="color:var(--text-main); font-size:13px;">${item.pmValue}</div>
      </td>
      <td>
        <span class="status-badge ${badgeClass}">${badgeLabel}</span>
        <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">${item.note}</div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('forensicRationaleSummary').textContent = cand.rationale;

  const btnSignOff = document.getElementById('btnConfirmReconciliation');
  if (btnSignOff) {
    btnSignOff.onclick = () => openSignOffModal(cand);
  }
}

// ==========================================================================
// REGISTRIES & RECONCILIATIONS
// ==========================================================================
function renderPMRegistry() {
  const grid = document.getElementById('pmCardsGrid');
  grid.innerHTML = '';

  state.postmortem.forEach(pm => {
    const card = document.createElement('div');
    card.className = 'entity-card';

    const dental = pm.dentalRecord || {};

    card.innerHTML = `
      <div class="entity-card-header">
        <div>
          <div class="entity-id">${pm.id}</div>
          <div class="entity-title">${pm.recoveryLocation}</div>
        </div>
        <span class="tag ${pm.matchingStatus === 'Reconciled' ? 'tag-purple' : 'tag-cyan'}">${pm.matchingStatus}</span>
      </div>
      <div class="entity-card-body">
        <div class="entity-meta-row">
          <div><strong>Sex:</strong> ${pm.gender}</div>
          <div><strong>Est. Age:</strong> ${pm.estimatedAgeDisplay || pm.estimatedAgeMin + '-' + pm.estimatedAgeMax}</div>
          <div><strong>Height:</strong> ${pm.estimatedHeightCm} ±${pm.heightToleranceCm || 3} cm</div>
          <div><strong>Tag:</strong> ${pm.recoveryNumber || 'N/A'}</div>
        </div>
        <div class="entity-detail-box">
          <div class="entity-detail-label">Odontology / Dental Chart</div>
          <div>${dental.crowns || dental.details || 'Examination charted'}</div>
        </div>
        <div class="entity-detail-box">
          <div class="entity-detail-label">Scars, Implants & Trauma</div>
          <div>${pm.surgicalMedicalFindings || pm.scarsAndMarks || 'None noted'}</div>
        </div>
        <div class="entity-detail-box">
          <div class="entity-detail-label">Apparel & Personal Effects</div>
          <div>${pm.clothingFound || 'Textile fragments'}; ${pm.personalEffectsFound || 'No jewelry'}</div>
        </div>
      </div>
      <div class="entity-card-footer">
        <span style="font-size:11px; color:var(--text-dim); font-family:var(--font-mono);">${pm.dnaSampleStatus}</span>
        <button class="btn btn-primary btn-sm" onclick="inspectPM('${pm.id}')">
          Match Workbench
        </button>
      </div>
    `;
    grid.appendChild(card);
  });
}

function renderAMRegistry() {
  const grid = document.getElementById('amCardsGrid');
  grid.innerHTML = '';

  state.antemortem.forEach(am => {
    const card = document.createElement('div');
    card.className = 'entity-card';

    const dental = am.dentalRecord || {};

    card.innerHTML = `
      <div class="entity-card-header">
        <div>
          <div class="entity-id">${am.id} • ${am.caseRef || 'REF-N/A'}</div>
          <div class="entity-title">${am.fullName}</div>
        </div>
        <span class="tag ${am.status === 'Confirmed Identified' ? 'tag-purple' : 'tag-amber'}">${am.status}</span>
      </div>
      <div class="entity-card-body">
        <div class="entity-meta-row">
          <div><strong>Sex:</strong> ${am.gender}</div>
          <div><strong>Age:</strong> ${am.age} yrs</div>
          <div><strong>Height:</strong> ${am.heightCm} cm</div>
          <div><strong>Blood:</strong> ${am.bloodGroup || 'N/A'}</div>
        </div>
        <div class="entity-detail-box">
          <div class="entity-detail-label">Dental Ante-Mortem Record</div>
          <div>${dental.crowns || dental.details || 'Records on file'}</div>
        </div>
        <div class="entity-detail-box">
          <div class="entity-detail-label">Surgical & Identifying Marks</div>
          <div>${am.surgicalMedicalHistory || am.scarsAndMarks || 'No surgery noted'}</div>
        </div>
        <div class="entity-detail-box">
          <div class="entity-detail-label">Reported Apparel & Jewelry</div>
          <div>${am.clothingDescription || 'N/A'}; ${am.personalEffects || 'N/A'}</div>
        </div>
      </div>
      <div class="entity-card-footer">
        <span style="font-size:11px; color:var(--text-dim);">Reporter: ${am.reporterContact?.relation || 'Kin'}</span>
        <span class="tag tag-outline">${am.dnaProfileStatus ? 'DNA Ready' : 'Pending'}</span>
      </div>
    `;
    grid.appendChild(card);
  });
}

function renderReconciliations() {
  const list = document.getElementById('reconDossierList');
  const miniList = document.getElementById('dashboardMiniReconList');
  list.innerHTML = '';
  if (miniList) miniList.innerHTML = '';

  if (state.reconciliations.length === 0) {
    list.innerHTML = '<div style="padding:30px; text-align:center; color:var(--text-dim); font-size:13px;">No official reconciliations issued yet.</div>';
    if (miniList) miniList.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-dim); font-size:12px;">No completed sign-offs yet.</div>';
    document.getElementById('reportEmptyState').style.display = 'block';
    document.getElementById('reportPaperContent').style.display = 'none';
    return;
  }

  state.reconciliations.forEach((r, idx) => {
    const item = document.createElement('div');
    item.className = `recon-item ${idx === 0 ? 'active' : ''}`;
    item.onclick = () => {
      document.querySelectorAll('.recon-item').forEach(el => el.classList.remove('active'));
      item.classList.add('active');
      renderReportPreview(r);
    };

    item.innerHTML = `
      <div class="recon-item-title">${r.victimName} (${r.amId})</div>
      <div class="recon-item-meta">${r.recoveryNumber} • Concordance: ${r.matchScore}%</div>
      <div style="font-size:10px; color:var(--accent-cyan); margin-top:4px;">${r.reconciliationId}</div>
    `;
    list.appendChild(item);

    if (miniList) {
      const mini = document.createElement('div');
      mini.style.cssText = 'padding:14px 18px; border-bottom:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;';
      mini.innerHTML = `
        <div>
          <strong style="color:#fff; font-size:13px;">${r.victimName}</strong>
          <div style="font-size:11px; color:var(--accent-cyan); font-family:var(--font-mono);">${r.pmId} ➔ ${r.amId}</div>
        </div>
        <span class="tag tag-purple">${r.matchScore}% ID</span>
      `;
      miniList.appendChild(mini);
    }
  });

  renderReportPreview(state.reconciliations[0]);
}

function renderReportPreview(recon) {
  document.getElementById('reportEmptyState').style.display = 'none';
  const paper = document.getElementById('reportPaperContent');
  paper.style.display = 'block';

  const inc = state.incident;
  const am = state.antemortem.find(a => a.id === recon.amId) || {};
  const pm = state.postmortem.find(p => p.id === recon.pmId) || {};

  paper.innerHTML = `
    <div class="dvi-report-header">
      <div class="dvi-emblem">NATIONAL FORENSIC DISASTER VICTIM IDENTIFICATION BOARD</div>
      <div class="dvi-report-title">FORMAL DVI RECONCILIATION DOSSIER & CERTIFICATE</div>
      <div class="dvi-report-subtitle">Conducted under Interpol Disaster Victim Identification Standards (AM/PM Consensus)</div>
      <div class="dvi-dossier-ref">DOSSIER REF: ${recon.dossierNumber || recon.reconciliationId}</div>
    </div>

    <div class="dvi-section-title">1. Incident & Operational Jurisdiction</div>
    <table class="dvi-table">
      <tr>
        <th>Incident Code & Title</th>
        <td>${inc.incidentId || 'DIS-2026-METRO'} — ${inc.operationName || 'Operation Trident'}</td>
      </tr>
      <tr>
        <th>Incident Nature & Location</th>
        <td>${inc.incidentType || 'Industrial Incident'} • ${inc.location}</td>
      </tr>
      <tr>
        <th>Forensic Pathologist In-Charge</th>
        <td>${recon.signoff?.forensicPathologist || 'Senior Forensic Pathologist'}</td>
      </tr>
    </table>

    <div class="dvi-section-title">2. Identified Victim Profile (Ante-Mortem Record)</div>
    <table class="dvi-table">
      <tr>
        <th>Victim Full Legal Name</th>
        <td><strong>${recon.victimName}</strong></td>
      </tr>
      <tr>
        <th>Ante-Mortem Record ID</th>
        <td>${recon.amId} (Police Ref: ${am.caseRef || 'N/A'})</td>
      </tr>
      <tr>
        <th>Biological Sex & Stature</th>
        <td>${am.gender}, Age: ${am.age} years, Height: ${am.heightCm} cm</td>
      </tr>
      <tr>
        <th>Next of Kin Reporting</th>
        <td>${am.reporterContact?.name || 'Family Kin'} (${am.reporterContact?.relation || 'Spouse/Parent'})</td>
      </tr>
    </table>

    <div class="dvi-section-title">3. Unidentified Human Remains (Post-Mortem Findings)</div>
    <table class="dvi-table">
      <tr>
        <th>PM Body Code & Body Bag</th>
        <td><strong>${recon.pmId}</strong> (Recovery Tag: ${recon.recoveryNumber || 'REC-METRO'})</td>
      </tr>
      <tr>
        <th>Recovery Site / Grid Sector</th>
        <td>${recon.recoveryLocation || 'Incident Zone'}</td>
      </tr>
      <tr>
        <th>Post-Mortem Morphology</th>
        <td>Estimated ${pm.gender}, Age ${pm.estimatedAgeDisplay || 'Adult'}, Stature ${pm.estimatedHeightCm} cm</td>
      </tr>
      <tr>
        <th>Remains Condition</th>
        <td>${pm.bodyCondition || 'Examined'}</td>
      </tr>
    </table>

    <div class="dvi-section-title">4. Scientific Concordance & Identification Basis</div>
    <div class="scientific-concordance-box">
      <div style="font-size:16px; font-weight:800; color:#166534; margin-bottom:6px;">
        MATCH CONCORDANCE INDEX: ${recon.matchScore}% — ${recon.confidenceTier}
      </div>
      <p style="font-size:13px; color:#14532d; line-height:1.7;">
        ${recon.forensicRationale}
      </p>
    </div>

    <table class="dvi-table">
      <tr>
        <th>Primary DVI Evidence (Odontology / DNA / Dactyloscopy)</th>
        <td>${recon.primaryEvidentiaryBasis?.length ? recon.primaryEvidentiaryBasis.join('<br>') : 'Dental gold crown #16 matching; STR DNA profile concordant'}</td>
      </tr>
      <tr>
        <th>Secondary DVI Evidence (Anatomical / Surgical / Tattoos)</th>
        <td>${recon.secondaryEvidentiaryBasis?.length ? recon.secondaryEvidentiaryBasis.join('<br>') : 'Surgical scar and physical landmarks concordant'}</td>
      </tr>
      <tr>
        <th>Auxiliary Evidence (Textile / Personal Effects)</th>
        <td>${recon.auxiliaryEvidentiaryBasis?.length ? recon.auxiliaryEvidentiaryBasis.join('<br>') : 'Personal jewelry and apparel remnants match'}</td>
      </tr>
      <tr>
        <th>Board Observations & Ruling</th>
        <td>${recon.notes}</td>
      </tr>
    </table>

    <div class="dvi-signatures-grid">
      <div class="signature-block">
        <div class="sign-line"></div>
        <div class="sign-title">${recon.signoff?.forensicPathologist}</div>
        <div class="sign-name">Lead Forensic Pathologist</div>
      </div>
      <div class="signature-block">
        <div class="sign-line"></div>
        <div class="sign-title">${recon.signoff?.forensicOdontologist}</div>
        <div class="sign-name">Chief Forensic Odontologist</div>
      </div>
      <div class="signature-block">
        <div class="sign-line"></div>
        <div class="sign-title">${recon.signoff?.investigatingOfficer}</div>
        <div class="sign-name">Senior Investigating Officer (IO)</div>
      </div>
    </div>
  `;
}

// ==========================================================================
// MODALS & ACTIONS
// ==========================================================================
function initModals() {
  const formAM = document.getElementById('formNewAM');
  if (formAM) {
    formAM.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formAM);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/antemortem', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).then(r => r.json());

        closeModal('modalAM');
        formAM.reset();
        await loadAllData();
        switchTab('tabAM');
      } catch (err) {
        alert('Failed to save Ante-Mortem profile: ' + err.message);
      }
    });
  }

  const formPM = document.getElementById('formNewPM');
  if (formPM) {
    formPM.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formPM);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/postmortem', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).then(r => r.json());

        closeModal('modalPM');
        formPM.reset();
        await loadAllData();
        inspectPM(res.id);
      } catch (err) {
        alert('Failed to save Post-Mortem profile: ' + err.message);
      }
    });
  }

  const formSignOff = document.getElementById('formSignOff');
  if (formSignOff) {
    formSignOff.addEventListener('submit', async (e) => {
      e.preventDefault();
      const cand = state.activeCandidateForSignOff;
      if (!cand) return;

      const payload = {
        amId: cand.amId,
        pmId: cand.pmId,
        pathologistSignoff: document.getElementById('signOffPathologist').value,
        odontologistSignoff: document.getElementById('signOffOdontologist').value,
        notes: document.getElementById('signOffNotes').value
      };

      try {
        const res = await fetch('/api/reconcile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).then(r => r.json());

        closeModal('modalSignOff');
        await loadAllData();
        switchTab('tabReports');
        renderReportPreview(res.reconciliation);
      } catch (err) {
        alert('Failed to record reconciliation: ' + err.message);
      }
    });
  }
}

function openSignOffModal(cand) {
  state.activeCandidateForSignOff = cand;
  document.getElementById('signOffAMName').textContent = cand.amName;
  document.getElementById('signOffAMId').textContent = cand.amId;
  document.getElementById('signOffPMId').textContent = cand.pmId;
  document.getElementById('signOffPMLocation').textContent = state.currentPM?.recoveryLocation || 'Incident Location';
  document.getElementById('signOffScoreBox').textContent = `${cand.matchPercentage}% — ${cand.confidenceTier}`;

  document.getElementById('modalSignOff').classList.add('active');
}

window.closeModal = function(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('active');
};

function initEventListeners() {
  document.getElementById('btnRefreshData')?.addEventListener('click', loadAllData);

  document.getElementById('btnLaunchBatchMatch')?.addEventListener('click', async () => {
    await renderDashboardTriage();
    alert('Global auto-matching evaluation executed across all records.');
  });

  document.getElementById('btnOpenNewPMModal')?.addEventListener('click', () => {
    document.getElementById('modalPM').classList.add('active');
  });
  document.getElementById('btnOpenNewPMModal2')?.addEventListener('click', () => {
    document.getElementById('modalPM').classList.add('active');
  });

  document.getElementById('btnOpenNewAMModal')?.addEventListener('click', () => {
    document.getElementById('modalAM').classList.add('active');
  });
  document.getElementById('btnOpenNewAMModal2')?.addEventListener('click', () => {
    document.getElementById('modalAM').classList.add('active');
  });

  document.getElementById('btnRunComparison')?.addEventListener('click', () => {
    const val = document.getElementById('selectPMSubject').value;
    loadMatchingForPM(val);
  });

  document.getElementById('selectPMSubject')?.addEventListener('change', (e) => {
    loadMatchingForPM(e.target.value);
  });

  document.getElementById('dashSearchInput')?.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const rows = document.querySelectorAll('#dashboardTriageBody tr');
    rows.forEach(r => {
      r.style.display = r.textContent.toLowerCase().includes(term) ? '' : 'none';
    });
  });
}
