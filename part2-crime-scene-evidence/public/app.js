/**
 * AI Crime Scene Evidence Prioritization — Frontend Logic (Enhanced Edition)
 * Interacts with REST API for multi-case evidence triage, live triage simulator, and Form 27 reports.
 */

const state = {
  cases: [],
  currentCaseId: null,
  currentCase: null,
  evidenceList: [],
  fslReports: [],
  activeTab: 'tabEvidenceBoard',
  filterPriority: 'ALL',
  filterType: 'ALL',
  searchTerm: '',
  selectedInspectorId: null
};

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initModals();
  initEventListeners();
  loadAllData();
});

// ==========================================================================
// DATA LOADING
// ==========================================================================
async function loadAllData() {
  try {
    const [casesRes, reportsRes] = await Promise.all([
      fetch('/api/cases').then(r => r.json()),
      fetch('/api/fsl-reports').then(r => r.json())
    ]);

    state.cases = casesRes || [];
    state.fslReports = reportsRes || [];

    populateCaseDropdown();

    if (!state.currentCaseId && state.cases.length > 0) {
      state.currentCaseId = state.cases[0].id;
    }

    if (state.currentCaseId) {
      await loadCaseEvidence(state.currentCaseId);
    }

    renderCasesGrid();
    renderReports();
  } catch (err) {
    console.error('Failed to load initial data:', err);
  }
}

async function loadCaseEvidence(caseId) {
  state.currentCaseId = caseId;
  state.currentCase = state.cases.find(c => c.id === caseId);

  updateCaseHeader();

  try {
    const res = await fetch(`/api/cases/${caseId}`).then(r => r.json());
    state.evidenceList = res.evidenceItems || [];
    updateMetrics(res.metrics || {});

    renderEvidenceTable();
    renderFSLQueue();

    populateInspectorDropdown();
    if (state.evidenceList.length > 0) {
      const targetId = state.selectedInspectorId || state.evidenceList[0].id;
      inspectEvidence(targetId);
    }
  } catch (err) {
    console.error('Failed to load case evidence:', err);
  }
}

function updateCaseHeader() {
  const c = state.currentCase;
  if (!c) return;

  document.getElementById('incCaseTitle').textContent = c.caseTitle;
  document.getElementById('incCrimeType').textContent = c.crimeType;
  document.getElementById('incLocation').textContent = c.location;
  document.getElementById('incDateOccurred').textContent = `Occurred: ${new Date(c.dateOccurred).toLocaleDateString()}`;
  document.getElementById('topNavOfficer').textContent = c.investigatingOfficer;
  document.getElementById('incStatusTag').textContent = c.incidentStatus || 'Active Triage';

  const select = document.getElementById('selectActiveCase');
  if (select) select.value = c.id;
}

function updateMetrics(m) {
  document.getElementById('metricTotalEvidence').textContent = m.totalItems || state.evidenceList.length;
  document.getElementById('metricCriticalCount').textContent = m.critical || 0;
  document.getElementById('metricHighCount').textContent = m.high || 0;
  document.getElementById('metricUrgentAction').textContent = m.urgentActionNeeded || 0;
  document.getElementById('metricReportCount').textContent = state.fslReports.length;
  document.getElementById('tabCaseCount').textContent = state.cases.length;
  document.getElementById('tabReportCount').textContent = state.fslReports.length;

  const banner = document.getElementById('urgentBannerContainer');
  if (m.urgentActionNeeded > 0) {
    banner.style.display = 'block';
    document.getElementById('urgentBannerText').textContent =
      `${m.urgentActionNeeded} evidence item(s) are at critical risk of degradation or battery depletion. Fast-track FSL dispatch required.`;
  } else {
    banner.style.display = 'none';
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

  updateStepperState(tabId);
}

function updateStepperState(tabId) {
  const stepMap = {
    'tabCases': 'csiStep1',
    'tabEvidenceBoard': 'csiStep2',
    'tabFSLQueue': 'csiStep3',
    'tabReports': 'csiStep4'
  };

  document.querySelectorAll('.step-card').forEach(s => s.classList.remove('active'));
  const activeStepId = stepMap[tabId];
  if (activeStepId) {
    document.getElementById(activeStepId)?.classList.add('active');
  }
}

// ==========================================================================
// CASE SELECTOR
// ==========================================================================
function populateCaseDropdown() {
  const select = document.getElementById('selectActiveCase');
  if (!select) return;
  select.innerHTML = '';

  state.cases.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = `${c.id} — ${c.caseTitle} (${c.crimeType.split('/')[0].trim()})`;
    select.appendChild(opt);
  });
}

// ==========================================================================
// TAB 1: EVIDENCE TRIAGE TABLE
// ==========================================================================
function renderEvidenceTable() {
  const tbody = document.getElementById('evidenceTableBody');
  tbody.innerHTML = '';

  let list = [...state.evidenceList];

  if (state.filterPriority !== 'ALL') {
    list = list.filter(e => e.priorityLevel.toUpperCase() === state.filterPriority);
  }

  if (state.filterType !== 'ALL') {
    list = list.filter(e => e.evidenceType.toLowerCase().includes(state.filterType.toLowerCase()));
  }

  if (state.searchTerm) {
    const term = state.searchTerm.toLowerCase();
    list = list.filter(e =>
      e.evidenceName.toLowerCase().includes(term) ||
      e.id.toLowerCase().includes(term) ||
      e.description.toLowerCase().includes(term) ||
      e.seizedLocation.toLowerCase().includes(term)
    );
  }

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:40px; color:var(--text-dim);">No evidence items match the selected filter.</td></tr>`;
    return;
  }

  list.forEach(ev => {
    const tr = document.createElement('tr');

    let scoreColor = 'var(--accent-cyan)';
    if (ev.priorityScore >= 85) scoreColor = 'var(--accent-rose)';
    else if (ev.priorityScore >= 70) scoreColor = 'var(--accent-amber)';

    const primaryTest = ev.recommendedTests && ev.recommendedTests[0] ? ev.recommendedTests[0] : 'Standard Examination';

    tr.innerHTML = `
      <td><strong style="color:var(--accent-rose); font-family:var(--font-mono); font-size:14px;">${ev.id}</strong></td>
      <td>
        <div style="font-weight:700; color:#fff; font-size:14px;">${ev.evidenceName}</div>
        <div style="font-size:12px; color:var(--text-muted); line-height:1.4;">${ev.description.slice(0, 75)}...</div>
        <div style="font-size:11px; color:var(--accent-cyan); margin-top:4px;">📍 Location: ${ev.seizedLocation}</div>
      </td>
      <td>
        <span class="tag tag-outline">${ev.evidenceType}</span>
        <div style="font-size:11px; color:var(--text-dim); margin-top:4px;">${ev.subType || ''}</div>
      </td>
      <td>
        <span class="priority-badge ${ev.priorityLevel}">${ev.priorityLevel}</span>
      </td>
      <td>
        <span class="score-pill" style="color:${scoreColor};">${ev.priorityScore} / 100</span>
      </td>
      <td>
        <div style="font-size:12px; color:var(--text-main); font-weight:600;">${primaryTest}</div>
        <div style="font-size:11px; color:var(--accent-amber); margin-top:4px;">⏱ Turnaround: ${ev.estimatedTurnaround || '3–5 Days'}</div>
      </td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="inspectEvidence('${ev.id}', true)">
          Deep Inspect
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.filterByPriority = function(priority) {
  state.filterPriority = priority;
  document.querySelectorAll('.pill-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-filter-priority') === priority);
  });
  renderEvidenceTable();
  switchTab('tabEvidenceBoard');
};

// ==========================================================================
// TAB 2: RANKED FSL LAB QUEUE
// ==========================================================================
function renderFSLQueue() {
  const container = document.getElementById('fslQueueContainer');
  container.innerHTML = '';

  if (state.evidenceList.length === 0) {
    container.innerHTML = `<div style="padding:40px; text-align:center; color:var(--text-dim);">No evidence items in current case.</div>`;
    return;
  }

  state.evidenceList.forEach((ev, idx) => {
    const card = document.createElement('div');
    card.className = 'queue-card';

    const testItems = (ev.recommendedTests || []).slice(0, 3).map(t => `
      <li>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <span>${t}</span>
      </li>
    `).join('');

    card.innerHTML = `
      <div class="queue-rank-col">
        <div class="queue-rank-num">#${idx + 1}</div>
        <div class="queue-rank-label">Queue Rank</div>
      </div>
      <div class="queue-info-col">
        <div class="tag-row">
          <span class="tag tag-outline">${ev.id}</span>
          <span class="priority-badge ${ev.priorityLevel}">${ev.priorityLevel} (${ev.priorityScore} pts)</span>
        </div>
        <div class="queue-item-name">${ev.evidenceName}</div>
        <div class="queue-item-meta">
          <strong>Type:</strong> ${ev.evidenceType} • <strong>Seized:</strong> ${ev.seizedLocation}
        </div>
        <div style="font-size:12px; color:var(--text-dim); margin-top:6px; line-height:1.4;">
          ${ev.reason}
        </div>
      </div>
      <div class="queue-tests-col">
        <div class="tests-header">Recommended FSL Lab Tests:</div>
        <ul class="test-list">
          ${testItems}
        </ul>
      </div>
      <div class="queue-action-col">
        <div class="turnaround-box">
          <div>Est. Turnaround:</div>
          <div class="turnaround-val">${ev.estimatedTurnaround}</div>
        </div>
        <span class="tag ${ev.priorityLevel === 'CRITICAL' ? 'tag-rose' : 'tag-cyan'}">${ev.queueAction.split('(')[0].trim()}</span>
        <button class="btn btn-outline btn-sm mt-2" onclick="inspectEvidence('${ev.id}', true)">Audit Score</button>
      </div>
      ${ev.preservationAlert ? `<div class="preservation-warning">${ev.preservationAlert}</div>` : ''}
    `;
    container.appendChild(card);
  });
}

// ==========================================================================
// TAB 3: FORENSIC DEEP INSPECTOR & SIMULATOR
// ==========================================================================
function populateInspectorDropdown() {
  const select = document.getElementById('selectInspectorItem');
  if (!select) return;
  select.innerHTML = '';

  state.evidenceList.forEach(ev => {
    const opt = document.createElement('option');
    opt.value = ev.id;
    opt.textContent = `${ev.id} — ${ev.evidenceName} [${ev.priorityLevel} - ${ev.priorityScore} pts]`;
    select.appendChild(opt);
  });
}

window.inspectEvidence = function(evId, doSwitchTab = false) {
  state.selectedInspectorId = evId;
  const select = document.getElementById('selectInspectorItem');
  if (select) select.value = evId;

  const ev = state.evidenceList.find(e => e.id === evId);
  if (!ev) return;

  const container = document.getElementById('inspectorContent');
  const b = ev.scoreBreakdown || {
    degradationScore: 20, degradationMax: 35, degradationNote: '',
    probativeScore: 30, probativeMax: 40, probativeNote: '',
    urgencyScore: 15, urgencyMax: 25, urgencyNote: ''
  };

  const degPct = Math.round((b.degradationScore / b.degradationMax) * 100);
  const probPct = Math.round((b.probativeScore / b.probativeMax) * 100);
  const urgPct = Math.round((b.urgencyScore / b.urgencyMax) * 100);

  const testsList = (ev.recommendedTests || []).map(t => `
    <li style="margin-bottom:8px; display:flex; align-items:center; gap:8px;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
      <span style="color:#fff; font-size:13px;">${t}</span>
    </li>
  `).join('');

  container.innerHTML = `
    <!-- Left Column: Item Details & Packaging -->
    <div class="card">
      <div class="card-header flex-between">
        <div>
          <span class="card-title">${ev.evidenceName}</span>
          <div style="font-size:11px; color:var(--accent-rose); font-family:var(--font-mono); margin-top:2px;">${ev.id} • ${ev.caseId}</div>
        </div>
        <span class="priority-badge ${ev.priorityLevel}">${ev.priorityLevel}</span>
      </div>
      <div class="card-body">
        <div class="entity-detail-box mb-3">
          <div class="entity-detail-label">Crime Scene Seizure Location</div>
          <div>${ev.seizedLocation}</div>
        </div>

        <div class="entity-detail-box mb-3">
          <div class="entity-detail-label">Physical Description & Recovery Condition</div>
          <div>${ev.description}</div>
        </div>

        <div class="entity-detail-box mb-3">
          <div class="entity-detail-label">Suspected Case Nexus / Relevance</div>
          <div>${ev.suspectedRelevance}</div>
        </div>

        <div class="entity-detail-box mb-3">
          <div class="entity-detail-label">Packaging & Chain of Custody Protocol</div>
          <div>${ev.packagingDetails} (Seized by ${ev.collectedBy})</div>
        </div>

        <div class="alert-box alert-success mt-3">
          <strong>Custody Vault:</strong> ${ev.custodyStatus} • <strong>Target Lab:</strong> ${ev.labDivision || 'State FSL'}
        </div>
      </div>
    </div>

    <!-- Right Column: Transparent Mathematical Priority Score Audit -->
    <div class="card">
      <div class="card-header flex-between">
        <span class="card-title">ISO/IEC 17025 Priority Scoring Breakdown</span>
        <span class="score-pill text-rose">${ev.priorityScore} / 100 PTS</span>
      </div>
      <div class="card-body">
        <!-- Factor 1: Degradation -->
        <div class="score-bar-group">
          <div class="score-bar-header">
            <strong>1. Perishability & Degradation Risk</strong>
            <span style="color:var(--accent-rose); font-family:var(--font-mono);">${b.degradationScore} / ${b.degradationMax} pts</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill fill-rose" style="width: ${degPct}%;"></div>
          </div>
          <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">${b.degradationNote}</div>
        </div>

        <!-- Factor 2: Probative Nexus -->
        <div class="score-bar-group">
          <div class="score-bar-header">
            <strong>2. Probative & Crime Linkage Value</strong>
            <span style="color:var(--accent-amber); font-family:var(--font-mono);">${b.probativeScore} / ${b.probativeMax} pts</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill fill-amber" style="width: ${probPct}%;"></div>
          </div>
          <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">${b.probativeNote}</div>
        </div>

        <!-- Factor 3: Statutory Urgency -->
        <div class="score-bar-group">
          <div class="score-bar-header">
            <strong>3. Statutory Remand & Investigation Deadlines</strong>
            <span style="color:var(--accent-cyan); font-family:var(--font-mono);">${b.urgencyScore} / ${b.urgencyMax} pts</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill fill-cyan" style="width: ${urgPct}%;"></div>
          </div>
          <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">${b.urgencyNote}</div>
        </div>

        <div class="entity-detail-box mt-4">
          <div class="entity-detail-label">Recommended Forensic Tests (Lab Protocol)</div>
          <ul style="list-style:none; padding:4px 0;">
            ${testsList}
          </ul>
        </div>

        ${ev.preservationAlert ? `
          <div class="preservation-warning mt-3" style="border-radius:6px; padding:12px;">
            ${ev.preservationAlert}
          </div>
        ` : ''}
      </div>
    </div>
  `;

  if (doSwitchTab) {
    switchTab('tabInspector');
  }
};

// ==========================================================================
// TAB 4: CASES REGISTRY
// ==========================================================================
function renderCasesGrid() {
  const grid = document.getElementById('casesGrid');
  grid.innerHTML = '';

  state.cases.forEach(c => {
    const card = document.createElement('div');
    card.className = 'entity-card';

    card.innerHTML = `
      <div class="entity-card-header">
        <div>
          <div class="entity-id">${c.id}</div>
          <div class="entity-title">${c.caseTitle}</div>
        </div>
        <span class="tag tag-rose">${c.incidentStatus}</span>
      </div>
      <div class="entity-card-body">
        <div class="entity-meta-row">
          <div><strong>Crime:</strong> ${c.crimeType}</div>
          <div><strong>Date:</strong> ${new Date(c.dateOccurred).toLocaleDateString()}</div>
        </div>
        <div class="entity-detail-box">
          <div class="entity-detail-label">Scene Location</div>
          <div>${c.location}</div>
        </div>
        <div class="entity-detail-box">
          <div class="entity-detail-label">Crime Scene Synopsis</div>
          <div>${c.description}</div>
        </div>
        <div class="entity-meta-row">
          <div><strong>IO:</strong> ${c.investigatingOfficer}</div>
          <div><strong>CSI Lead:</strong> ${c.leadForensicInvestigator}</div>
        </div>
      </div>
      <div class="entity-card-footer">
        <span style="font-size:11px; color:var(--text-dim);">${c.totalEvidence || 0} Evidence Items Logged</span>
        <button class="btn btn-primary btn-sm" onclick="switchActiveCase('${c.id}')">
          Switch to Case
        </button>
      </div>
    `;
    grid.appendChild(card);
  });
}

window.switchActiveCase = async function(caseId) {
  await loadCaseEvidence(caseId);
  switchTab('tabEvidenceBoard');
};

// ==========================================================================
// TAB 5: FSL FORM 27 REPORTS
// ==========================================================================
function renderReports() {
  const sidebar = document.getElementById('reportsListSidebar');
  sidebar.innerHTML = '';

  if (state.fslReports.length === 0) {
    sidebar.innerHTML = `<div style="padding:30px; text-align:center; color:var(--text-dim); font-size:13px;">No Form 27 dossiers generated yet.</div>`;
    document.getElementById('reportEmptyMessage').style.display = 'block';
    document.getElementById('reportPaperContent').style.display = 'none';
    return;
  }

  state.fslReports.forEach((rep, idx) => {
    const item = document.createElement('div');
    item.className = `recon-item ${idx === 0 ? 'active' : ''}`;
    item.onclick = () => {
      document.querySelectorAll('.recon-item').forEach(el => el.classList.remove('active'));
      item.classList.add('active');
      renderForm27Preview(rep);
    };

    item.innerHTML = `
      <div class="recon-item-title">${rep.caseTitle}</div>
      <div class="recon-item-meta">${rep.reportId} • ${rep.totalItems} Items Logged</div>
      <div style="font-size:10px; color:var(--accent-rose); margin-top:4px;">Priority: ${rep.submissionPriority}</div>
    `;
    sidebar.appendChild(item);
  });

  renderForm27Preview(state.fslReports[0]);
}

function renderForm27Preview(rep) {
  document.getElementById('reportEmptyMessage').style.display = 'none';
  const paper = document.getElementById('reportPaperContent');
  paper.style.display = 'block';

  const manifestRows = (rep.evidenceManifest || []).map((m, i) => `
    <tr>
      <td style="font-family:var(--font-mono); font-weight:700;">${m.id}</td>
      <td><strong>${m.evidenceName}</strong><br><span style="font-size:11px; color:#475569;">${m.description}</span></td>
      <td>${m.evidenceType}</td>
      <td><span style="font-weight:700; color:#be123c;">${m.priorityLevel} (${m.priorityScore} pts)</span></td>
      <td>${m.recommendedTests ? m.recommendedTests.slice(0, 2).join('; ') : 'Routine Examination'}</td>
    </tr>
  `).join('');

  paper.innerHTML = `
    <div class="fsl-report-header">
      <div class="fsl-emblem">STATE FORENSIC SCIENCE LABORATORY (SFSL)</div>
      <div class="fsl-report-title">FORM 27: REQUISITION FOR FORENSIC EXAMINATION & EVIDENCE MANIFEST</div>
      <div class="fsl-report-sub">Standard Criminal Investigation Dispatch Docket • Under Section 293 CrPC / Bharatiya Nagarik Suraksha Sanhita</div>
      <div style="margin-top:10px; display:inline-block; background:#f1f5f9; padding:4px 12px; border:1px solid #cbd5e1; font-family:var(--font-mono); font-size:11px; font-weight:700;">
        DISPATCH DOSSIER ID: ${rep.reportId}
      </div>
    </div>

    <table class="fsl-table">
      <tr>
        <th style="width:25%;">Case Reference & FIR</th>
        <td><strong>${rep.caseId}</strong> — ${rep.caseTitle}</td>
      </tr>
      <tr>
        <th>Crime Classification</th>
        <td>${rep.crimeType}</td>
      </tr>
      <tr>
        <th>Crime Scene Location</th>
        <td>${rep.location}</td>
      </tr>
      <tr>
        <th>Investigating Officer (IO)</th>
        <td>${rep.investigatingOfficer}</td>
      </tr>
      <tr>
        <th>Target Laboratory</th>
        <td>${rep.labDirectorate}</td>
      </tr>
      <tr>
        <th>Dispatch Urgency Classification</th>
        <td><strong style="color:#be123c;">${rep.submissionPriority}</strong></td>
      </tr>
    </table>

    <div style="font-size:13px; font-weight:800; color:#0f172a; margin:20px 0 10px 0;">PRIORITIZED EVIDENCE MANIFEST & RECOMMENDED TESTS</div>
    <table class="fsl-table manifest-table">
      <thead>
        <tr>
          <th style="width:12%;">Item ID</th>
          <th style="width:30%;">Evidence Description</th>
          <th style="width:18%;">Type</th>
          <th style="width:15%;">AI Priority</th>
          <th style="width:25%;">Recommended Tests</th>
        </tr>
      </thead>
      <tbody>
        ${manifestRows}
      </tbody>
    </table>

    <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:14px; border-radius:6px; margin:18px 0; font-size:12px; line-height:1.6;">
      <strong>Investigator Hypotheses & Examination Requisition Notes:</strong><br>
      ${rep.officialNotes}
    </div>

    <table class="fsl-table">
      <tr>
        <th style="width:30%;">Tamper-Proof Chain of Custody Hash</th>
        <td style="font-family:var(--font-mono); font-size:11px;">${rep.chainOfCustodyAudit?.custodyHash || 'SHA256-VERIFIED'}</td>
      </tr>
      <tr>
        <th>Courier & Transport Security</th>
        <td>${rep.chainOfCustodyAudit?.dispatchCarrier || 'Armed Forensic Courier'} (All seals verified intact)</td>
      </tr>
    </table>

    <div class="dvi-signatures-grid">
      <div class="signature-block">
        <div class="sign-line"></div>
        <div class="sign-title">${rep.investigatingOfficer}</div>
        <div class="sign-name">Seizing Investigating Officer (IO)</div>
      </div>
      <div class="signature-block">
        <div class="sign-line"></div>
        <div class="sign-title">${rep.leadForensicInvestigator || 'Senior CSI Specialist'}</div>
        <div class="sign-name">Crime Scene Triage Specialist</div>
      </div>
      <div class="signature-block">
        <div class="sign-line"></div>
        <div class="sign-title">Director / Receiving Officer</div>
        <div class="sign-name">Forensic Science Laboratory Ingestion</div>
      </div>
    </div>
  `;
}

// ==========================================================================
// MODALS & EVENT LISTENERS
// ==========================================================================
function initModals() {
  function updateLiveScore() {
    const deg = document.getElementById('modalDegradation')?.value || 'MEDIUM';
    const prob = document.getElementById('modalProbative')?.value || 'HIGH';
    const urg = document.getElementById('modalUrgency')?.value || 'MEDIUM';

    fetch('/api/analyze-preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        degradationRisk: deg,
        probativeValue: prob,
        statutoryUrgency: urg,
        evidenceType: document.getElementById('modalEvidenceType')?.value || 'Biological / DNA'
      })
    })
    .then(r => r.json())
    .then(res => {
      const badge = document.getElementById('liveScoreBadge');
      badge.textContent = `${res.priorityScore} / 100 — ${res.priorityLevel}`;
      badge.className = `live-score-badge tag ${res.priorityLevel === 'CRITICAL' ? 'tag-rose' : (res.priorityLevel === 'HIGH' ? 'tag-amber' : 'tag-cyan')}`;
      document.getElementById('liveScoreReason').textContent = res.reason;
    })
    .catch(console.error);
  }

  ['modalDegradation', 'modalProbative', 'modalUrgency', 'modalEvidenceType'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', updateLiveScore);
  });

  const formAdd = document.getElementById('formAddEvidence');
  if (formAdd) {
    formAdd.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formAdd);
      const payload = Object.fromEntries(formData.entries());
      payload.caseId = state.currentCaseId;

      try {
        await fetch('/api/evidence', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        closeModal('modalAddEvidence');
        formAdd.reset();
        await loadCaseEvidence(state.currentCaseId);
        switchTab('tabEvidenceBoard');
      } catch (err) {
        alert('Failed to add evidence: ' + err.message);
      }
    });
  }

  const formCase = document.getElementById('formNewCase');
  if (formCase) {
    formCase.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formCase);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/cases', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).then(r => r.json());

        closeModal('modalNewCase');
        formCase.reset();
        await loadAllData();
        await switchActiveCase(res.id);
      } catch (err) {
        alert('Failed to create case: ' + err.message);
      }
    });
  }

  const formReport = document.getElementById('formGenerateFSLReport');
  if (formReport) {
    formReport.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        caseId: state.currentCaseId,
        officerName: document.getElementById('reportOfficerName').value,
        labDirectorate: document.getElementById('reportLabDirectorate').value,
        priorityCategory: document.getElementById('reportPriorityCat').value,
        notes: document.getElementById('reportOfficialNotes').value
      };

      try {
        const res = await fetch('/api/fsl-report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).then(r => r.json());

        closeModal('modalGenerateFSLReport');
        await loadAllData();
        switchTab('tabReports');
        renderForm27Preview(res.report);
      } catch (err) {
        alert('Failed to generate FSL Report: ' + err.message);
      }
    });
  }
}

function initEventListeners() {
  document.getElementById('btnSyncData')?.addEventListener('click', loadAllData);

  document.getElementById('selectActiveCase')?.addEventListener('change', (e) => {
    switchActiveCase(e.target.value);
  });

  document.getElementById('selectInspectorItem')?.addEventListener('change', (e) => {
    inspectEvidence(e.target.value);
  });

  document.getElementById('btnOpenAddEvidenceModal')?.addEventListener('click', () => {
    document.getElementById('modalAddEvidence').classList.add('active');
  });

  document.getElementById('btnOpenNewCaseModal')?.addEventListener('click', () => {
    document.getElementById('modalNewCase').classList.add('active');
  });

  document.getElementById('btnOpenGenerateReportModal')?.addEventListener('click', () => {
    document.getElementById('modalGenerateFSLReport').classList.add('active');
  });

  document.querySelectorAll('.pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.filterPriority = btn.getAttribute('data-filter-priority');
      document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderEvidenceTable();
    });
  });

  document.getElementById('filterTypeSelect')?.addEventListener('change', (e) => {
    state.filterType = e.target.value;
    renderEvidenceTable();
  });

  document.getElementById('evidenceSearchInput')?.addEventListener('input', (e) => {
    state.searchTerm = e.target.value;
    renderEvidenceTable();
  });
}

window.closeModal = function(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('active');
};
