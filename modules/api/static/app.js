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
                allow_weak_sedation_docs: document.getElementById('coder-weak-sedation').checked
            };
        } else if (currentMode === 'registry') {
            url = '/v1/registry/run';
            payload = {
                note: text,
                explain: document.getElementById('registry-explain').checked
            };
        } else if (currentMode === 'reporter') {
            url = '/v1/reporter/generate';
            payload = {
                note: text,
                template: document.getElementById('reporter-template').value
            };
        }

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        lastResult = await response.json();
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

        if (lastResult.explanation) {
             html += `<hr><h5>Explanation</h5><pre>${lastResult.explanation}</pre>`;
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
        // Reporter formatting
        // lastResult.report (string markdown) and lastResult.struct (json)
        if (lastResult.report) {
            // Use marked to render markdown
            html = `<h4>Generated Report</h4><div class="border p-3 bg-white">${marked.parse(lastResult.report)}</div>`;
            html += `<hr><h5>Structured Data</h5><pre>${JSON.stringify(lastResult.struct, null, 2)}</pre>`;
            area.innerHTML = html;
        } else {
            area.innerHTML = `<p>No report generated.</p>`;
        }
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
