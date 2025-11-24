// Global state
let currentMode = 'coder';
let lastResult = null;

function ensureReporterTemplates() {
    const sel = document.getElementById('reporter-template');
    if (!sel) return;
    const desired = [
        { value: 'knowledge', label: 'Comprehensive (knowledge)' },
        { value: 'comprehensive', label: 'Comprehensive (alias)' },
        { value: 'comprehensive_ip', label: 'Comprehensive IP (alias)' },
    ];
    desired.forEach(({ value, label }) => {
        if (!Array.from(sel.options).some(opt => opt.value === value)) {
            const opt = document.createElement('option');
            opt.value = value;
            opt.textContent = label;
            sel.appendChild(opt);
        }
    });
}

function setMode(mode) {
    currentMode = mode;
    
    // Update Tab UI
    document.querySelectorAll('#mode-tabs .nav-link').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.mode === mode) el.classList.add('active');
    });

    // Update Options UI
    document.querySelectorAll('.mode-opt').forEach(el => el.style.display = 'none');
    document.getElementById(`opt-${mode}`).style.display = 'block';
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
    document.querySelector('button').disabled = show;
}

async function postJSON(url, payload) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (!response.ok) {
        const text = await response.text();
        throw new Error(`API Error: ${response.status} ${response.statusText} - ${text}`);
    }
    return response.json();
}

async function runReporterFlow(noteText) {
    // Step 1: registry extraction
    const extraction = await postJSON('/v1/registry/run', {
        note: noteText,
        explain: document.getElementById('registry-explain')?.checked || false,
    });

    // Step 2: validation/inference
    const verify = await postJSON('/report/verify', { extraction });

    // Step 3: render (empty patch by default)
    const render = await postJSON('/report/render', {
        bundle: verify.bundle,
        patch: { procedures: [] },
        embed_metadata: false,
        strict: false,
    });

    return { extraction, verify, render };
}

async function run() {
    const text = document.getElementById('input-text').value;
    if (!text.trim()) {
        alert("Please enter a procedure note.");
        return;
    }

    showLoading(true);
    
    try {
        let url, payload;

        if (currentMode === 'coder') {
            url = '/v1/coder/run';
            payload = {
                note: text,
                explain: document.getElementById('coder-explain').checked,
                allow_weak_sedation_docs: document.getElementById('coder-weak-sedation').checked,
                locality: document.getElementById('coder-locality').value || '00',
                setting: document.getElementById('coder-setting').value || 'facility'
            };
        } else if (currentMode === 'registry') {
            url = '/v1/registry/run';
            payload = {
                note: text,
                explain: document.getElementById('registry-explain').checked
            };
        } else if (currentMode === 'reporter') {
            lastResult = await runReporterFlow(text);
            renderResult();
            return;
        }

        lastResult = await postJSON(url, payload);
        console.log('API Response:', lastResult);
        console.log('Has financials:', !!lastResult.financials);
        if (lastResult.financials) {
            console.log('Financials data:', lastResult.financials);
        }
        renderResult();

    } catch (error) {
        document.getElementById('result-area').innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    } finally {
        showLoading(false);
    }
}

function renderResult() {
    // Show tabs
    document.getElementById('result-tabs').style.visibility = 'visible';
    
    // Default to formatted view
    showResultTab('formatted');
}

function showResultTab(tab) {
    // Update tab UI
    document.querySelectorAll('#result-tabs .nav-link').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');

    const area = document.getElementById('result-area');
    
    if (tab === 'json') {
        area.innerHTML = `<pre>${JSON.stringify(lastResult, null, 2)}</pre>`;
        return;
    }

    // Formatted View Logic
    if (currentMode === 'coder') {
        // Coder formatting
        let html = `<h4>Billing Codes</h4>`;
        if (lastResult.codes && lastResult.codes.length > 0) {
             html += `<ul class="list-group mb-3">`;
             lastResult.codes.forEach(code => {
                 html += `<li class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${code.code || code.cpt}</strong> - ${code.description || 'No description'}
                                ${code.modifiers && code.modifiers.length ? `<br><small class="text-muted">Modifiers: ${code.modifiers.join(', ')}</small>` : ''}
                            </div>
                            <span class="badge bg-primary rounded-pill">${code.quantity || 1}</span>
                          </li>`;
             });
             html += `</ul>`;
        } else {
            html += `<p class="text-muted">No codes generated.</p>`;
        }

        // Display RVU/Financials data if available
        // Always show financials section if it exists (even if empty)
        if (lastResult.financials !== undefined && lastResult.financials !== null) {
            const fin = lastResult.financials;
            const totalWorkRVU = (fin.total_work_rvu !== undefined && fin.total_work_rvu !== null) ? fin.total_work_rvu.toFixed(2) : 'N/A';
            // Use total_facility_payment as the primary estimate
            const totalPayment = (fin.total_facility_payment !== undefined && fin.total_facility_payment !== null) ? fin.total_facility_payment.toFixed(2) : 'N/A';
            
            html += `<hr><h5>RVU & Payment Information</h5>`;
            html += `<div class="card mb-3">`;
            html += `<div class="card-body">`;
            html += `<div class="row mb-3">`;
            html += `<div class="col-md-6"><strong>Total Work RVU:</strong> ${totalWorkRVU}</div>`;
            html += `<div class="col-md-6"><strong>Estimated Payment (Facility):</strong> $${totalPayment}</div>`;
            html += `</div>`;
            
            // Use per_code (list of PerCodeBilling) instead of breakdown
            if (fin.per_code && Array.isArray(fin.per_code) && fin.per_code.length > 0) {
                html += `<hr><h6>Per-Procedure Breakdown</h6>`;
                html += `<table class="table table-sm table-striped">`;
                html += `<thead><tr><th>CPT Code</th><th>Work RVU</th><th>Facility Pay</th></tr></thead>`;
                html += `<tbody>`;
                fin.per_code.forEach(proc => {
                    const workRVU = (proc.work_rvu !== undefined && proc.work_rvu !== null) ? proc.work_rvu.toFixed(2) : 'N/A';
                    // Use allowed_facility_payment
                    const payment = (proc.allowed_facility_payment !== undefined && proc.allowed_facility_payment !== null) ? proc.allowed_facility_payment.toFixed(2) : 'N/A';
                    
                    html += `<tr>`;
                    html += `<td><code>${proc.cpt_code || 'N/A'}</code></td>`;
                    html += `<td>${workRVU}</td>`;
                    html += `<td>$${payment}</td>`;
                    html += `</tr>`;
                });
                html += `</tbody></table>`;
            } else if (fin.total_work_rvu === 0 && fin.total_facility_payment === 0) {
                html += `<p class="text-muted mb-0">No RVU calculations available (no billable codes found).</p>`;
            }
            html += `</div></div>`;
        } else {
            html += `<hr><div class="alert alert-info">RVU calculations not available.</div>`;
        }

        if (lastResult.explanation) {
             html += `<hr><h5>Explanation</h5><pre>${lastResult.explanation}</pre>`;
        }
        
        // Display warnings if any
        if (lastResult.warnings && lastResult.warnings.length > 0) {
            html += `<hr><h5>Warnings</h5>`;
            html += `<div class="alert alert-warning">`;
            lastResult.warnings.forEach(warning => {
                html += `<div>${warning}</div>`;
            });
            html += `</div>`;
        }
        
        area.innerHTML = html;

    } else if (currentMode === 'registry') {
        // Registry formatting
        // It returns a flat dict usually representing the registry columns + evidence
        // Let's try to display key-value pairs nicely
        let html = `<h4>Registry Record</h4>`;
        html += `<table class="table table-striped table-sm"><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>`;
        
        for (const [key, value] of Object.entries(lastResult)) {
            if (key === 'evidence') continue; // Skip evidence in main table
            html += `<tr><td><code>${key}</code></td><td>${value}</td></tr>`;
        }
        html += `</tbody></table>`;

        if (lastResult.evidence) {
            html += `<h5>Evidence</h5><pre>${JSON.stringify(lastResult.evidence, null, 2)}</pre>`;
        }
        
        area.innerHTML = html;

    } else if (currentMode === 'reporter') {
        const { extraction, verify, render } = lastResult || {};
        const issues = render?.issues || verify?.issues || [];
        const warnings = render?.warnings || verify?.warnings || [];
        const inferenceNotes = render?.inference_notes || verify?.inference_notes || [];
        const suggestions = render?.suggestions || verify?.suggestions || [];

        let html = "";

        html += `<h4>Reporter Flow</h4>`;
        html += `<p class="text-muted small">Registry extraction → verify → render</p>`;

        if (render?.markdown) {
            html += `<div class="mb-3"><h5>Rendered Markdown</h5><div class="border p-3 bg-white">${marked.parse(render.markdown)}</div></div>`;
        } else {
            html += `<div class="alert alert-warning">Report not rendered yet (critical issues or validation warnings must be resolved).</div>`;
        }

        if (issues && issues.length) {
            html += `<h6>Issues</h6><ul class="list-group mb-3">`;
            issues.forEach(issue => {
                html += `<li class="list-group-item d-flex justify-content-between align-items-start">
                    <div>
                        <div><strong>${issue.proc_id || issue.proc_type}</strong>: ${issue.message || issue.field_path}</div>
                        <small class="text-muted">Severity: ${issue.severity}</small>
                    </div>
                    <span class="badge bg-${issue.severity === 'critical' ? 'danger' : 'warning'} text-uppercase">${issue.severity}</span>
                </li>`;
            });
            html += `</ul>`;
        }

        if (warnings && warnings.length) {
            html += `<h6>Warnings</h6><div class="alert alert-warning">${warnings.map(w => `<div>${w}</div>`).join("")}</div>`;
        }

        if (suggestions && suggestions.length) {
            html += `<h6>Suggestions</h6><div class="alert alert-info">${suggestions.map(s => `<div>${s}</div>`).join("")}</div>`;
        }

        if (inferenceNotes && inferenceNotes.length) {
            html += `<h6>Inference Notes</h6><div class="alert alert-info">${inferenceNotes.map(n => `<div>${n}</div>`).join("")}</div>`;
        }

        if (verify?.bundle) {
            html += `<h6>Bundle</h6><pre class="bg-light p-2 border rounded">${JSON.stringify(verify.bundle, null, 2)}</pre>`;
        }

        if (extraction) {
            html += `<h6>Registry Extraction</h6><pre class="bg-light p-2 border rounded">${JSON.stringify(extraction, null, 2)}</pre>`;
        }

        area.innerHTML = html;
    }
}

// Check API status on load
fetch('/health')
    .then(r => r.json())
    .then(data => {
        const badge = document.getElementById('api-status');
        if (data.ok) {
            badge.className = 'badge bg-success';
            badge.textContent = 'API Online';
        } else {
            badge.className = 'badge bg-danger';
            badge.textContent = 'API Error';
        }
    })
    .catch(() => {
        const badge = document.getElementById('api-status');
        badge.className = 'badge bg-danger';
        badge.textContent = 'API Offline';
    });

// Ensure reporter template dropdown includes all options even if the HTML was cached
ensureReporterTemplates();
