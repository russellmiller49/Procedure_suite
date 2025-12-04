// Minimal PHI demo client (synthetic data only). No logging of raw PHI.

const api = {
    async preview(text, document_type = null, specialty = null) {
        const resp = await fetch("/v1/phi/scrub/preview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, document_type, specialty }),
        });
        if (!resp.ok) throw new Error("Preview failed");
        return resp.json();
    },
    async submit(text, submitted_by = "demo_physician", document_type = null, specialty = null) {
        const resp = await fetch("/v1/phi/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, submitted_by, document_type, specialty }),
        });
        if (!resp.ok) throw new Error("Submit failed");
        return resp.json();
    },
    async status(procedure_id) {
        const resp = await fetch(`/v1/phi/status/${procedure_id}`);
        if (!resp.ok) throw new Error("Status lookup failed");
        return resp.json();
    },
    async procedure(procedure_id) {
        const resp = await fetch(`/v1/phi/procedure/${procedure_id}`);
        if (!resp.ok) throw new Error("Procedure lookup failed");
        return resp.json();
    },
    async feedback(procedure_id, payload) {
        const resp = await fetch(`/v1/phi/procedure/${procedure_id}/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (!resp.ok) throw new Error("Feedback failed");
        return resp.json();
    },
    async reidentify(procedure_id) {
        const resp = await fetch("/v1/phi/reidentify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ procedure_id, user_id: "phi_demo_user" }),
        });
        if (!resp.ok) throw new Error("Reidentify failed");
        return resp.json();
    },
    async listCases() {
        const resp = await fetch("/api/v1/phi-demo/cases");
        if (!resp.ok) throw new Error("Case list failed");
        return resp.json();
    },
    async createCase(payload) {
        const resp = await fetch("/api/v1/phi-demo/cases", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (!resp.ok) throw new Error("Create case failed");
        return resp.json();
    },
    async attachProcedure(case_id, procedure_id) {
        const resp = await fetch(`/api/v1/phi-demo/cases/${case_id}/procedure`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ procedure_id }),
        });
        if (!resp.ok) throw new Error("Attach procedure failed");
        return resp.json();
    },
};

const state = {
    preview: null,
    procedureId: null,
    scrubbedText: null,
    entities: [],
};

function $(id) {
    return document.getElementById(id);
}

function setStatus(text, cls = "bg-secondary") {
    const el = $("phi-status");
    el.textContent = text;
    el.className = `badge ${cls}`;
}

function renderPreview(result) {
    const preview = $("scrubbed-preview");
    preview.textContent = result.scrubbed_text;
    preview.classList.remove("text-muted");
    const list = $("entity-list");
    list.innerHTML = "";
    (result.entities || []).forEach((ent) => {
        const badge = document.createElement("span");
        badge.className = "badge bg-info text-dark entity-badge";
        badge.textContent = `${ent.entity_type} → ${ent.placeholder}`;
        list.appendChild(badge);
    });
    $("preview-meta").textContent = `${(result.entities || []).length} entities`;
}

function renderStatus(status, procedureId) {
    $("procedure-id").textContent = procedureId || "-";
    $("procedure-status").textContent = status || "-";
}

function renderCases(cases) {
    const list = $("case-list");
    list.innerHTML = "";
    cases.forEach((c) => {
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.innerHTML = `<div>
            <div class="fw-semibold">${c.scenario_label || "Demo case"}</div>
            <div class="small text-muted">${c.synthetic_patient_label || ""} • ${c.procedure_date || ""} • ${c.operator_name || ""}</div>
            <div class="small">procedure_id: ${c.procedure_id || "-"}</div>
        </div>
        <button class="btn btn-sm btn-outline-primary">Load</button>`;
        li.querySelector("button").onclick = async () => {
            if (c.procedure_id) {
                state.procedureId = c.procedure_id;
                renderStatus("loading...", state.procedureId);
                try {
                    const proc = await api.procedure(c.procedure_id);
                    state.scrubbedText = proc.scrubbed_text;
                    state.entities = proc.entities;
                    renderPreview(proc);
                    renderStatus(proc.status, c.procedure_id);
                    $("btn-refresh-status").disabled = false;
                    $("btn-mark-reviewed").disabled = false;
                    $("btn-reidentify").disabled = false;
                } catch (err) {
                    setStatus("Case load failed", "bg-danger");
                }
            }
        };
        list.appendChild(li);
    });
}

async function handlePreview() {
    const text = $("note-input").value || "";
    if (!text.trim()) {
        setStatus("Enter synthetic note text", "bg-warning text-dark");
        return;
    }
    setStatus("Previewing...", "bg-info text-dark");
    try {
        const res = await api.preview(text);
        state.preview = res;
        state.scrubbedText = res.scrubbed_text;
        state.entities = res.entities || [];
        renderPreview(res);
        $("btn-submit").disabled = false;
        setStatus("Preview complete", "bg-success");
    } catch (err) {
        setStatus("Preview failed", "bg-danger");
    }
}

async function handleSubmit() {
    const text = $("note-input").value || "";
    if (!state.preview) {
        setStatus("Run preview first", "bg-warning text-dark");
        return;
    }
    setStatus("Submitting...", "bg-info text-dark");
    try {
        const res = await api.submit(text, "demo_physician");
        state.procedureId = res.procedure_id;
        renderStatus(res.status, res.procedure_id);
        $("btn-refresh-status").disabled = false;
        $("btn-mark-reviewed").disabled = false;
        $("btn-reidentify").disabled = true; // only after review
        // Attach procedure_id to latest created case if any
        const cases = await api.listCases();
        if (cases.length > 0) {
            const latest = cases[cases.length - 1];
            if (!latest.procedure_id) {
                await api.attachProcedure(latest.id, res.procedure_id);
                loadCases();
            }
        }
        setStatus("Submitted", "bg-success");
    } catch (err) {
        setStatus("Submit failed", "bg-danger");
    }
}

async function handleStatus() {
    if (!state.procedureId) return;
    try {
        const res = await api.status(state.procedureId);
        renderStatus(res.status, res.procedure_id || state.procedureId);
        setStatus("Status refreshed", "bg-secondary");
    } catch (err) {
        setStatus("Status error", "bg-danger");
    }
}

async function handleReview() {
    if (!state.procedureId || !state.scrubbedText) return;
    setStatus("Marking reviewed...", "bg-info text-dark");
    try {
        const res = await api.feedback(state.procedureId, {
            scrubbed_text: state.scrubbedText,
            entities: state.entities || [],
            reviewer_id: "reviewer_demo",
            reviewer_email: "reviewer@example.com",
            reviewer_role: "physician",
            comment: "Auto-confirmed in demo",
        });
        renderStatus(res.status, state.procedureId);
        $("btn-reidentify").disabled = false;
        setStatus("Reviewed", "bg-success");
    } catch (err) {
        setStatus("Review failed", "bg-danger");
    }
}

async function handleReidentify() {
    if (!state.procedureId) return;
    setStatus("Reidentifying...", "bg-warning text-dark");
    try {
        const res = await api.reidentify(state.procedureId);
        $("reid-text").value = res.raw_text || "";
        setStatus("Reidentified", "bg-success");
    } catch (err) {
        setStatus("Reidentify failed", "bg-danger");
    }
}

async function loadCases() {
    try {
        const cases = await api.listCases();
        renderCases(cases);
    } catch (err) {
        setStatus("Case list failed", "bg-danger");
    }
}

async function createCase() {
    const scenarios = [
        "EBUS for RUL nodule",
        "Pleural effusion thoracentesis",
        "Bronchoscopy BAL follow-up",
    ];
    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    try {
        await api.createCase({
            synthetic_patient_label: "Patient X",
            procedure_date: dayjs().format("YYYY-MM-DD"),
            operator_name: "Dr. Jane Test",
            scenario_label: scenario,
        });
        loadCases();
        setStatus("Case created", "bg-success");
    } catch (err) {
        setStatus("Case create failed", "bg-danger");
    }
}

function init() {
    $("btn-preview").onclick = handlePreview;
    $("btn-submit").onclick = handleSubmit;
    $("btn-refresh-status").onclick = handleStatus;
    $("btn-mark-reviewed").onclick = handleReview;
    $("btn-reidentify").onclick = handleReidentify;
    $("btn-create-case").onclick = createCase;
    loadCases();
}

document.addEventListener("DOMContentLoaded", init);
