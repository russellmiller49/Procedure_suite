import React, {useEffect, useMemo, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import {api} from "./api";
import {Compare, type Comparison} from "./Compare";
import {LaunchReview} from "./LaunchReview";
import {Measures, type Analysis} from "./Measures";
import {evidenceSpans, fresh, fromProposal, label} from "./review";
import {SourceView} from "./SourceView";
import type {CaseDetail, CaseRow, Profile, Run, SourceDocument, Span, Status, Values} from "./types";
import "./style.css";

type Page = "review" | "worklist" | "measures";
type Mode = "assisted" | "blinded";
const STATES = ["present", "absent", "unknown", "not_documented"];
const MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"];
const EFFORTS = ["low", "medium", "high", "xhigh", "max"];

function money(value: number | null) {
  return value == null ? "" : `$${value.toFixed(value < 0.01 ? 4 : 3)}`;
}

function RunCard({run, mode, drafting, selected, onToggle, onDraft, onFocus}: {
  run: Run;
  mode: Mode;
  drafting: boolean;
  selected: boolean;
  onToggle: () => void;
  onDraft: () => void;
  onFocus: (span: Span) => void;
}) {
  const hidden = mode === "blinded" && drafting;
  const unresolved = run.unresolved_mentions || [];
  const errors = run.contract_errors || [];
  return (
    <article className={"run " + run.status}>
      <div className="row-head">
        <h4>
          {run.provider === "claude" ? `${run.model} · ${run.effort}` : "Deterministic engine"}
        </h4>
        <span className={"chip " + run.status}>{run.status === "succeeded" ? run.proposal_status : run.status}</span>
      </div>
      <small>
        {new Date(run.created_at).toLocaleString()}
        {run.cost_usd != null && ` · ${money(run.cost_usd)}`}
        {run.latency_s != null && ` · ${run.latency_s.toFixed(1)}s`}
        {run.unresolved > 0 && ` · ${run.unresolved} unresolved`}
      </small>
      {run.error && <p className="field-alert">{run.error}</p>}
      {run.warnings?.length > 0 && <p className="subtle">{run.warnings.map(label).join(" · ")}</p>}
      {hidden ? (
        <p className="subtle">Proposals are hidden while a blinded draft is open.</p>
      ) : (
        run.status === "succeeded" && (
          <>
            {errors.length > 0 && <p className="field-alert">Contract errors: {errors.map(label).join(", ")}</p>}
            <div className="row">
              <button disabled={!run.has_proposal} onClick={onDraft}>Start assisted draft</button>
              <label className="check"><input type="checkbox" checked={selected} onChange={onToggle} />Compare</label>
            </div>
            {unresolved.length > 0 && (
              <details>
                <summary>Unresolved mentions ({unresolved.length})</summary>
                <ul className="unresolved">
                  {unresolved.map((u, i) => (
                    <li key={i}>
                      <strong>{label(u.kind)}</strong> {u.note}
                      {u.start != null && u.end != null && (
                        <button className="link" onClick={() => onFocus({document_id: run.document_id, start: u.start!, end: u.end!})}>show</button>
                      )}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </>
        )
      )}
    </article>
  );
}

function App() {
  const [page, setPage] = useState<Page>("review");
  const [status, setStatus] = useState<Status | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [split, setSplit] = useState("");
  const [query, setQuery] = useState("");
  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [document, setDocument] = useState<SourceDocument | null>(null);
  const [focus, setFocus] = useState<Span | null>(null);
  const [values, setValues] = useState<Values | null>(null);
  const [dirty, setDirty] = useState(false);
  const [mode, setMode] = useState<Mode>("assisted");
  const [sourceRuns, setSourceRuns] = useState<string[]>([]);
  const [selectedRuns, setSelectedRuns] = useState<string[]>([]);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [effort, setEffort] = useState("medium");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const queue = useRef<Promise<void>>(Promise.resolve());

  async function run(fn: () => Promise<void>) {
    const next = queue.current.then(async () => {
      setBusy(true);
      setError("");
      setMessage("");
      try {
        await fn();
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setBusy(false);
      }
    });
    queue.current = next;
    await next;
  }

  async function refreshCases() {
    const params = new URLSearchParams();
    if (split) params.set("split", split);
    if (query) params.set("q", query);
    setCases(await api<CaseRow[]>("/cases" + (params.size ? "?" + params : "")));
  }

  useEffect(() => {
    void run(async () => {
      setStatus(await api<Status>("/status"));
      setProfile(await api<Profile>("/profile"));
      await refreshCases();
    });
  }, []);
  useEffect(() => { void run(refreshCases); }, [split]);

  async function loadDocument(id: string) {
    setDocument(await api<SourceDocument>("/documents/" + id));
  }

  async function openCase(id: string, keepDraft = false) {
    const d = await api<CaseDetail>("/cases/" + id);
    setDetail(d);
    setComparison(null);
    setSelectedRuns([]);
    if (!keepDraft) {
      setValues(d.draft || d.approved || null);
      setMode((d.revisions.at(-1)?.mode as Mode) || "assisted");
      setSourceRuns([]);
      setDirty(false);
      setFocus(null);
      if (d.documents[0]) await loadDocument(d.documents[0].id);
      else setDocument(null);
    }
    setPage("review");
  }

  function edit(v: Values) {
    setValues(v);
    setDirty(true);
  }

  function focusSpan(span: Span) {
    setFocus(span);
    if (span.document_id && span.document_id !== document?.id) void run(() => loadDocument(span.document_id));
  }

  async function extract(provider: "deterministic" | "claude") {
    if (!document) return;
    const body = provider === "claude" ? {provider, model, effort} : {provider};
    let current = await api<Run>(`/documents/${document.id}/extractions`, "POST", body);
    setMessage(`${provider === "claude" ? model : "Deterministic"} extraction ${current.status}…`);
    while (current.status === "queued" || current.status === "running") {
      await new Promise(r => setTimeout(r, 1500));
      current = await api<Run>("/extractions/" + current.id);
    }
    await openCase(detail!.id, true);
    setMessage(`Extraction ${current.status}${current.cost_usd != null ? " · " + money(current.cost_usd) : ""}.`);
  }

  async function startAssisted(runId: string) {
    const r = await api<Run>("/extractions/" + runId);
    const proposal = r.response?.observations?.proposal;
    if (!proposal) throw new Error("This run has no proposal.");
    setValues(fromProposal(proposal, detail?.event_date || null));
    setMode("assisted");
    setSourceRuns([runId]);
    setDirty(true);
    setMessage("Assisted draft started from the proposal. Every value still needs review.");
  }

  function startBlinded() {
    setValues(fresh(detail?.event_date || ""));
    setMode("blinded");
    setSourceRuns([]);
    setDirty(true);
    setComparison(null);
    setMessage("Blinded draft started. Model proposals stay hidden until it is saved.");
  }

  async function save() {
    if (!detail || !values) return;
    await api(`/cases/${detail.id}/revisions`, "POST", {expected_version: detail.version, values, mode, source_run_ids: sourceRuns});
    await openCase(detail.id);
    await refreshCases();
    setMessage("Draft revision saved.");
  }

  async function approve() {
    if (!detail?.draft_revision_id) return;
    await api(`/cases/${detail.id}/approve`, "POST", {expected_version: detail.version, revision_id: detail.draft_revision_id});
    await openCase(detail.id);
    await refreshCases();
    setMessage("Revision approved.");
  }

  async function compare() {
    if (!detail) return;
    setComparison(await api<Comparison>(`/cases/${detail.id}/compare?runs=${selectedRuns.join(",")}`));
  }

  const runs = useMemo(() => (detail?.runs || []).filter(r => r.document_id === document?.id).reverse(), [detail, document]);
  const drafting = values != null && dirty;
  const filtered = cases.filter(c => !query || c.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <>
      <header>
        <div className="brand">IP / REGISTRY<span>Robotic bronchoscopy + linear EBUS · synthetic workbench</span></div>
        <span className="badge">Synthetic only</span>
        <span className={"badge " + (status?.claude_configured ? "ok" : "warn")}>
          Claude {status?.claude_configured ? "configured" : "not configured"}
        </span>
      </header>
      <nav aria-label="Workbench">
        {(["review", "worklist", "measures"] as Page[]).map(p => (
          <button
            key={p}
            className={page === p ? "active" : ""}
            onClick={() => run(async () => {
              setPage(p);
              if (p === "measures") setAnalysis(await api<Analysis>("/analysis"));
              if (p === "worklist") await refreshCases();
            })}
          >
            {p}
          </button>
        ))}
      </nav>
      <div className="status" role="status">{busy ? "Working…" : message}</div>
      {error && <div className="error" role="alert">{error}</div>}
      <main>
        {page === "worklist" && (
          <>
            <h1>Completeness worklist</h1>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Case</th><th>Platform</th><th>Split</th><th>Status</th><th>Documents</th><th>Missing</th></tr></thead>
                <tbody>
                  {filtered.map(c => (
                    <tr key={c.id} className="clickable" onClick={() => run(() => openCase(c.id))}>
                      <td>{c.label}</td><td>{c.platform}</td><td>{c.split}</td>
                      <td><span className={"chip " + c.status}>{c.status}</span></td>
                      <td className="num">{c.documents}</td><td>{c.missing.map(label).join(", ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
        {page === "measures" && (
          <>
            <h1>Launch measures</h1>
            <div className="row">
              <a className="button" href="/api/v1/workbench/export/gold.jsonl">Download approved revisions (JSONL)</a>
              {analysis && (
                <button onClick={() => {
                  const url = URL.createObjectURL(new Blob([JSON.stringify(analysis, null, 2)], {type: "application/json"}));
                  const a = window.document.createElement("a");
                  a.href = url;
                  a.download = "robotic-ebus-analysis-0.2.0.json";
                  a.click();
                  URL.revokeObjectURL(url);
                }}>
                  Download analysis tables
                </button>
              )}
            </div>
            {analysis ? <Measures analysis={analysis} /> : <p>Loading…</p>}
          </>
        )}
        {page === "review" && (
          <div className="workspace">
            <aside>
              <h2>Cases</h2>
              <label>Split
                <select value={split} onChange={e => setSplit(e.target.value)}>
                  <option value="">All</option>
                  {["train", "validation", "regression", "test"].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </label>
              <label>Search<input value={query} onChange={e => setQuery(e.target.value)} placeholder="Label" /></label>
              <div className="case-list">
                {filtered.map(c => (
                  <button key={c.id} className={detail?.id === c.id ? "case selected" : "case"} onClick={() => run(() => openCase(c.id))}>
                    <strong>{c.label}</strong>
                    <small>{c.platform || "—"} · <span className={"chip " + c.status}>{c.status}</span></small>
                  </button>
                ))}
                {!filtered.length && <p className="subtle">No cases. Seed with ops/tools/seed_registry_workbench.py.</p>}
              </div>
            </aside>
            {!detail || !profile ? (
              <section className="empty">
                <h1>Review with the source in view</h1>
                <p>Select a case. Run the deterministic engine or Claude on a document, start an assisted draft from a proposal or a blinded draft from nothing, then save and approve.</p>
              </section>
            ) : (
              <section>
                <div className="case-banner">
                  <strong>{detail.label}</strong>
                  <span>{detail.platform || "Unknown platform"} · {detail.split} · {detail.source}</span>
                  <span className={"chip " + (dirty ? "draft" : detail.status)}>{dirty ? "unsaved changes" : detail.status}</span>
                </div>
                <div className="review">
                  <section>
                    <h3>Source</h3>
                    <SourceView
                      documents={detail.documents}
                      document={document}
                      onSelect={id => run(() => loadDocument(id))}
                      spans={document ? evidenceSpans(values, document.id) : []}
                      focus={focus}
                    />
                    <h3>Extraction runs</h3>
                    <div className="row">
                      <button disabled={busy || !document} onClick={() => run(() => extract("deterministic"))}>Run deterministic</button>
                      <select aria-label="Claude model" value={model} onChange={e => setModel(e.target.value)}>
                        {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
                      </select>
                      <select aria-label="Effort" value={effort} onChange={e => setEffort(e.target.value)}>
                        {EFFORTS.map(m => <option key={m} value={m}>{m}</option>)}
                      </select>
                      <button
                        className="primary"
                        disabled={busy || !document || !status?.claude_configured}
                        title={status?.claude_configured ? "" : "Set ANTHROPIC_API_KEY on the server"}
                        onClick={() => run(() => extract("claude"))}
                      >
                        Run Claude
                      </button>
                    </div>
                    {runs.map(r => (
                      <RunCard
                        key={r.id}
                        run={r}
                        mode={mode}
                        drafting={drafting}
                        selected={selectedRuns.includes(r.id)}
                        onToggle={() => setSelectedRuns(s => (s.includes(r.id) ? s.filter(x => x !== r.id) : [...s, r.id]))}
                        onDraft={() => run(() => startAssisted(r.id))}
                        onFocus={focusSpan}
                      />
                    ))}
                    {!runs.length && <p className="subtle">No runs for this document yet.</p>}
                    {selectedRuns.length > 0 && !(mode === "blinded" && drafting) && (
                      <button onClick={() => run(compare)}>Compare selected{detail.draft || detail.approved ? " with saved revisions" : ""}</button>
                    )}
                    {comparison && <Compare comparison={comparison} />}
                  </section>
                  <section>
                    <h3>Registry values</h3>
                    {!values ? (
                      <div className="row">
                        <button onClick={startBlinded}>Start blinded draft</button>
                        <span className="subtle">or start an assisted draft from a run.</span>
                      </div>
                    ) : (
                      <>
                        <div className="row">
                          <span className="chip">{mode} review</span>
                          <label>Procedure date
                            <input type="date" value={values.event_date || ""} onChange={e => edit({...values, event_date: e.target.value})} />
                          </label>
                          <label>Immediate complication assessment
                            <select value={values.complication_assessment} onChange={e => edit({...values, complication_assessment: e.target.value})}>
                              {STATES.map(s => <option key={s} value={s}>{label(s)}</option>)}
                            </select>
                          </label>
                        </div>
                        <LaunchReview profile={profile} values={values} onChange={edit} onEvidence={focusSpan} disabled={busy} />
                        <div className="actions">
                          <button className="primary" disabled={busy || !dirty || !values.event_date} onClick={() => run(save)}>Save draft revision</button>
                          <button disabled={busy || dirty || !detail.draft_revision_id} onClick={() => run(approve)}>Approve draft</button>
                          <button disabled={busy} onClick={startBlinded}>Discard and start blinded</button>
                        </div>
                      </>
                    )}
                    <details>
                      <summary>Revision history ({detail.revisions.length})</summary>
                      {detail.revisions.map(r => (
                        <p key={r.id}>Revision {r.number} · {r.mode} · {r.approved_at ? "approved " + new Date(r.approved_at).toLocaleString() : "draft"}</p>
                      ))}
                    </details>
                  </section>
                </div>
              </section>
            )}
          </div>
        )}
      </main>
      <footer>Synthetic notes only · robotic_ebus_v1 contract 0.2.0 (same dictionary as the Epic app) · Not for clinical use · Prompt {status?.prompt_digest.slice(0, 12)}</footer>
    </>
  );
}

createRoot(window.document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
