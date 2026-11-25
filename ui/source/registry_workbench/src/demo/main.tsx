import React, {useEffect, useMemo, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import {Compare} from "../Compare";
import {label, segments} from "../review";
import "../style.css";
import "./demo.css";
import {CodesCard} from "./CodesCard";
import {DemoApiError, extract, getConfig, getSample, type DemoConfig, type ExtractResult, type SampleDetail} from "./demoApi";
import {FieldList} from "./FieldList";
import {buildSections, countStates} from "./fields";
import {applyRedactions, Redactor, ScanGate, type Detection} from "./phiRedaction";

type Phase = "original" | "scanning" | "reviewing" | "redacted";
type Tab = "fields" | "compare" | "codes";

function NoteView({text, spans, focus}: {text: string; spans: [number, number][]; focus: [number, number] | null}) {
  const marked = useRef<HTMLElement | null>(null);
  useEffect(() => {
    marked.current?.scrollIntoView({block: "center", behavior: "smooth"});
  }, [focus]);
  return (
    <pre className="source-text" aria-label="Note text">
      {segments(text, spans, focus).map(seg =>
        seg.mark === "none" ? (
          <span key={seg.start}>{seg.text}</span>
        ) : (
          <mark key={seg.start} className={seg.mark} ref={seg.mark === "focus" ? el => { if (el) marked.current = el; } : undefined}>
            {seg.text}
          </mark>
        ),
      )}
    </pre>
  );
}

function App() {
  const [config, setConfig] = useState<DemoConfig | null>(null);
  const [sample, setSample] = useState<SampleDetail | null>(null);
  const [text, setText] = useState("");
  const [phase, setPhase] = useState<Phase>("original");
  const [detections, setDetections] = useState<Detection[]>([]);
  const [excluded, setExcluded] = useState<Set<string>>(new Set());
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<ExtractResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [focus, setFocus] = useState<[number, number] | null>(null);
  const [tab, setTab] = useState<Tab>("fields");
  const [ready, setReady] = useState(false);
  const gate = useRef(new ScanGate());
  const redactor = useRef<Redactor | null>(null);
  const scanning = useRef(false);

  function resetReview(nextText: string) {
    gate.current.textChanged();
    redactor.current?.cancel();
    scanning.current = false;
    setText(nextText);
    setPhase("original");
    setDetections([]);
    setExcluded(new Set());
    setResult(null);
    setFocus(null);
    setReady(false);
    setStatus("");
    setError("");
  }

  async function choose(id: string) {
    try {
      const detail = await getSample(id);
      setSample(detail);
      resetReview(detail.text);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  useEffect(() => {
    getConfig()
      .then(c => {
        setConfig(c);
        if (c.samples.length) void choose(c.samples[0].id);
      })
      .catch(e => setError(e instanceof DemoApiError && e.status === 404 ? "The demo is not enabled on this server." : String(e.message || e)));
    return () => redactor.current?.dispose();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function runDetection() {
    if (!redactor.current) {
      redactor.current = new Redactor(event => {
        // After a cancel the worker still reports loading progress; ignore it.
        if (event.type === "status" || event.type === "progress") {
          if (scanning.current) setStatus(event.message);
        } else if (event.type === "ready") {
          if (scanning.current) setStatus("Local model loaded. Scanning…");
        } else if (event.type === "error") {
          scanning.current = false;
          setError(`De-identification could not run: ${event.message}`);
          setPhase("original");
        } else if (event.type === "done") {
          // A cancelled or outdated scan still reports "done" with partial results; drop it.
          if (!gate.current.accept(event.scanId)) return;
          scanning.current = false;
          setDetections(event.detections);
          setExcluded(new Set());
          setPhase("reviewing");
          setStatus(`Scan complete: ${event.detections.length} item${event.detections.length === 1 ? "" : "s"} found.`);
        }
      });
    }
    setError("");
    setPhase("scanning");
    scanning.current = true;
    redactor.current.scan(gate.current.begin(), text);
  }

  function cancelScan() {
    gate.current.cancel();
    redactor.current?.cancel();
    scanning.current = false;
    setPhase("original");
    setStatus("Scan cancelled. Nothing was applied.");
  }

  function apply() {
    const redacted = applyRedactions(text, detections, excluded);
    gate.current.markApplied();
    setText(redacted);
    setDetections([]);
    setPhase("redacted");
    setReady(gate.current.readyToExtract);
    setStatus("Redactions applied in this browser.");
  }

  function useReviewed() {
    const reviewed = sample?.reviewed_redactions[0];
    if (!reviewed) return;
    redactor.current?.cancel();
    scanning.current = false;
    gate.current.cancel();
    gate.current.markReviewedText();
    setText(reviewed.text);
    setDetections([]);
    setPhase("redacted");
    setResult(null);
    setReady(gate.current.readyToExtract);
    setStatus("Showing the reviewed redaction of this sample.");
    setError("");
  }

  async function runExtract() {
    if (!gate.current.readyToExtract) return;
    setBusy(true);
    setError("");
    try {
      setResult(await extract(text, sample?.id ?? null));
      setTab("fields");
    } catch (e) {
      setResult(null);
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const reviewedTexts = useMemo(() => new Set((sample?.reviewed_redactions || []).map(r => r.text.trimEnd())), [sample]);
  const matchesReviewed = phase === "redacted" && reviewedTexts.has(text.trimEnd());
  const sections = useMemo(
    () => (config && result?.llm?.proposal ? buildSections(config.profile, result.llm.proposal) : []),
    [config, result],
  );
  const counts = useMemo(() => countStates(sections), [sections]);
  // Before applying, the detected identifiers are marked. After extraction only the passage
  // the reader clicked is marked, so one fact maps to one visible quote.
  const noteSpans: [number, number][] = detections.filter(d => !excluded.has(d.id)).map(d => [d.start, d.end] as [number, number]);
  const inference = result?.llm?.inference || {};
  const summary = result?.comparison.summary;

  return (
    <>
      <header>
        <div className="brand">
          ROBOTIC BRONCHOSCOPY + LINEAR EBUS
          <span>Registry extraction demo · synthetic notes only</span>
        </div>
        <span className="badge warn">Prototype</span>
        <a className="headlink" href="/ui/dashboard.html">Full coding dashboard</a>
      </header>
      <main className="demo">
        <p className="notice" role="note">
          {config?.notice || "Prototype on synthetic notes only. Not clinically validated."}
        </p>
        {error && <div className="error" role="alert">{error}</div>}

        <section className="step">
          <h2><span className="num">1</span> Choose a synthetic note</h2>
          <div className="samples">
            {(config?.samples || []).map(s => (
              <button key={s.id} className={"sample" + (sample?.id === s.id ? " selected" : "")} onClick={() => void choose(s.id)}>
                <strong>{s.title}</strong>
                <small>{s.teaching_point}</small>
                {!s.has_result && <small className="pending">Result not yet generated</small>}
              </button>
            ))}
          </div>
          {config && !config.live_extraction.enabled && (
            <p className="subtle">This release runs the bundled samples only. Pasting your own synthetic note comes with the access-code release.</p>
          )}
        </section>

        <div className="review">
          <section>
            <section className="step">
              <h2><span className="num">2</span> De-identify in this browser</h2>
              <p className="subtle">
                Detection runs locally. Only the redacted text is sent for extraction.
                {phase === "redacted" ? " Shown below is the redacted text." : ""}
              </p>
              <div className="row">
                {phase === "scanning" ? (
                  <button onClick={cancelScan}>Cancel scan</button>
                ) : (
                  <button className={phase === "original" ? "primary" : ""} disabled={!text || phase === "redacted"} onClick={runDetection}>
                    Run detection
                  </button>
                )}
                <button className={phase === "reviewing" ? "primary" : ""} disabled={phase !== "reviewing"} onClick={apply}>
                  Apply redactions
                </button>
                {phase === "redacted" && sample && <button onClick={() => resetReview(sample.text)}>Start over</button>}
                {sample && sample.reviewed_redactions.length > 0 && !matchesReviewed && (
                  <button className="link" onClick={useReviewed}>Use the reviewed redaction</button>
                )}
              </div>
              {status && <p className="status-line" role="status">{status}</p>}
              {phase === "reviewing" && (
                <ul className="detections" aria-label="Detected identifiers">
                  {detections.length === 0 && <li className="subtle">Nothing was detected. Apply to confirm the text as it is.</li>}
                  {detections.map(d => (
                    <li key={d.id}>
                      <label className="check">
                        <input
                          type="checkbox"
                          checked={!excluded.has(d.id)}
                          onChange={e => {
                            const next = new Set(excluded);
                            if (e.target.checked) next.delete(d.id);
                            else next.add(d.id);
                            setExcluded(next);
                          }}
                        />
                        <span className="chip">{label(d.label.toLowerCase())}</span>&nbsp;{text.slice(d.start, d.end)}
                      </label>
                    </li>
                  ))}
                </ul>
              )}
              {phase === "redacted" && sample && sample.reviewed_redactions.length > 0 && !matchesReviewed && (
                <p className="notice" role="note">
                  This redaction differs from the reviewed version of the sample. Stored results exist only for the reviewed
                  redaction, so extraction will not return a result for this text.
                </p>
              )}
            </section>
            <NoteView text={text} spans={noteSpans} focus={focus} />
          </section>

          <section>
            <section className="step">
              <h2><span className="num">3</span> Extract registry fields</h2>
              <div className="row">
                <button className="primary" disabled={!ready || busy} onClick={() => void runExtract()}>
                  {busy ? "Extracting…" : "Extract"}
                </button>
                {!ready && <span className="subtle">Apply redactions first.</span>}
              </div>
            </section>
            {result && (
              <>
                <p className="result-meta">
                  <span className="chip proposed">{result.source_label}</span>{" "}
                  {inference.model ? `${inference.model}${inference.effort ? " · " + inference.effort + " effort" : ""}` : "No model result stored"}
                  {result.generated_at ? ` · generated ${result.generated_at.slice(0, 10)}` : ""}
                  {result.llm?.status && result.llm.status !== "proposed" ? ` · ${result.llm.status}` : ""}
                </p>
                {!result.llm?.proposal && (
                  <p className="notice" role="note">
                    No model result is stored for this sample yet. The rules-engine result is in the comparison tab.
                  </p>
                )}
                {summary && result.llm?.proposal && (
                  <p className="tally">
                    <strong>{counts.value + counts.negative}</strong> values with a supporting passage
                    {counts.stated_missing > 0 && <> · <strong>{counts.stated_missing}</strong> stated as unknown or not done</>}
                    {counts.conflict > 0 && <> · <strong>{counts.conflict}</strong> unclear</>}
                    <br />
                    Side by side, the LLM filled <strong>{summary.llm_total}</strong> fields and the rules engine <strong>{summary.rules_total}</strong>.
                  </p>
                )}
                <div className="tabs" role="tablist">
                  {(["fields", "compare", "codes"] as Tab[]).map(t => (
                    <button key={t} role="tab" aria-selected={tab === t} className={tab === t ? "tab active" : "tab"} onClick={() => setTab(t)}>
                      {t === "fields" ? "Registry fields" : t === "compare" ? "LLM vs rules engine" : result.codes?.title || "Suggested codes"}
                    </button>
                  ))}
                </div>
                {tab === "fields" && (
                  result.llm?.proposal ? (
                    <>
                      <FieldList sections={sections} text={text} onFocus={setFocus} />
                      {result.llm.unresolved_mentions.length > 0 && (
                        <section>
                          <h3>Mentioned but not recorded</h3>
                          <p className="subtle">Planned, historical or uncertain statements are listed here and never turned into values.</p>
                          <ul className="unresolved">
                            {result.llm.unresolved_mentions.map((u, i) => (
                              <li key={i}>
                                <strong>{label(u.kind)}</strong> {u.note}{" "}
                                {u.start != null && u.end != null && (
                                  <button className="link" onClick={() => setFocus([u.start!, u.end!])}>show in note</button>
                                )}
                              </li>
                            ))}
                          </ul>
                        </section>
                      )}
                    </>
                  ) : (
                    <p className="subtle">No stored model result for this sample yet.</p>
                  )
                )}
                {tab === "compare" && (
                  <>
                    <p className="subtle">
                      Rows are matched on what a reviewer would match them on (lobe, station, tool). &ldquo;Not extracted&rdquo; means
                      that source returned nothing for the field; it is not a statement about the note.
                    </p>
                    <Compare comparison={result.comparison} blank="Not extracted" />
                  </>
                )}
                {tab === "codes" && (result.codes ? <CodesCard codes={result.codes} text={text} onFocus={setFocus} /> : <p className="subtle">No codes without a model result.</p>)}
              </>
            )}
          </section>
        </div>
      </main>
      <footer>Synthetic data only. Software prototype for demonstration; outputs require clinician and coder review.</footer>
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
