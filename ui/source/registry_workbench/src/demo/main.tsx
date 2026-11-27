import React, {useEffect, useMemo, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import {Compare} from "../Compare";
import {label, segments} from "../review";
import "../style.css";
import "./demo.css";
import {CodesCard} from "./CodesCard";
import {
  DemoApiError, extract, getConfig, getSample, recode, unlock,
  type Codes, type DemoConfig, type ExtractResult, type NoteKind, type SampleDetail, type TesterAccess,
} from "./demoApi";
import {FieldList} from "./FieldList";
import {buildSections, countRules, countStates, mentionsView} from "./fields";
import {applyRedactions, manualDetection, redactSpan, Redactor, ScanGate, selectionSpan, type Detection} from "./phiRedaction";
import {changesRecord, countReview, EMPTY_REVIEW, reviewedRecord, type Review} from "./reviewState";

type Phase = "original" | "scanning" | "reviewing" | "redacted";
type Tab = "fields" | "compare" | "codes";
type Source = "samples" | "own";

const ATTESTATION: Record<NoteKind, string> = {
  synthetic: "This note is synthetic. It describes no real patient.",
  real_redacted: "I have read the redacted text on the left and no patient identifiers remain.",
};

function NoteView({text, spans, focus, onSelect}: {
  text: string;
  spans: [number, number][];
  focus: [number, number] | null;
  onSelect?: (span: [number, number] | null) => void;
}) {
  const marked = useRef<HTMLElement | null>(null);
  const root = useRef<HTMLPreElement | null>(null);
  useEffect(() => {
    marked.current?.scrollIntoView({block: "center", behavior: "smooth"});
  }, [focus]);
  const report = onSelect ? () => onSelect(selectionSpan(root.current)) : undefined;
  return (
    <pre className="source-text" aria-label="Note text" ref={root} onMouseUp={report} onKeyUp={report}>
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
  const [source, setSource] = useState<Source>("samples");
  const [codeInput, setCodeInput] = useState("");
  const [access, setAccess] = useState<TesterAccess | null>(null);
  const [accessCode, setAccessCode] = useState("");
  const [unlockError, setUnlockError] = useState("");
  const [noteKind, setNoteKind] = useState<NoteKind>("synthetic");
  const [draft, setDraft] = useState("");
  const [ownText, setOwnText] = useState<string | null>(null);
  const [attested, setAttested] = useState(false);
  const [selection, setSelection] = useState<[number, number] | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [review, setReview] = useState<Review>(EMPTY_REVIEW);
  const [reviewedCodes, setReviewedCodes] = useState<Codes | null>(null);
  const [codesError, setCodesError] = useState("");
  const [recoding, setRecoding] = useState(false);
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
    setAttested(false);
    setSelection(null);
    clearFindingsReview();
  }

  function clearFindingsReview() {
    setReview(EMPTY_REVIEW);
    setReviewedCodes(null);
    setCodesError("");
  }

  function changeReview(next: Review) {
    setReview(next);
    // Codes worked out from an earlier state of the review no longer describe it.
    setReviewedCodes(null);
    setCodesError("");
  }

  async function choose(id: string) {
    try {
      const detail = await getSample(id);
      setSample(detail);
      setOwnText(null);
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

  async function submitCode() {
    setUnlockError("");
    try {
      setAccess(await unlock(codeInput));
      setAccessCode(codeInput.trim());
      setCodeInput("");
    } catch (e) {
      setUnlockError(e instanceof Error ? e.message : String(e));
    }
  }

  function useOwnNote() {
    if (!draft.trim()) return;
    setSample(null);
    setOwnText(draft);
    resetReview(draft);
  }

  /** Redact text the scan missed: listed with the detections before applying, replaced at once after. */
  function redactSelection() {
    if (!selection) return;
    if (phase === "reviewing") {
      const added = manualDetection(selection[0], selection[1]);
      if (!detections.some(d => d.id === added.id)) setDetections([...detections, added].sort((a, b) => a.start - b.start));
      setStatus("Added your selection to the items to redact.");
    } else if (phase === "redacted") {
      gate.current.markManualEdit();
      setText(redactSpan(text, selection));
      setResult(null);
      setFocus(null);
      setAttested(false);
      clearFindingsReview();
      setReady(gate.current.readyToExtract);
      setStatus("Your selection was redacted in this browser.");
    }
    setSelection(null);
    window.getSelection()?.removeAllRanges();
  }

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
    if (own && !attested) return;
    setBusy(true);
    setError("");
    setElapsed(0);
    clearFindingsReview();
    const started = Date.now();
    const timer = window.setInterval(() => setElapsed(Math.round((Date.now() - started) / 1000)), 1000);
    try {
      const live = own ? {access_code: accessCode, note_kind: noteKind, attested} : undefined;
      setResult(await extract(text, sample?.id ?? null, live));
      setTab("fields");
    } catch (e) {
      setResult(null);
      if (e instanceof DemoApiError && e.code === "bad_access_code") setAccess(null);
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      window.clearInterval(timer);
      setBusy(false);
    }
  }

  async function updateCodes() {
    if (!shownSide?.proposal) return;
    setRecoding(true);
    setCodesError("");
    try {
      setReviewedCodes(await recode(reviewedRecord(shownSide.proposal, review), shownSide.unresolved_mentions));
    } catch (e) {
      setCodesError(e instanceof Error ? e.message : String(e));
    } finally {
      setRecoding(false);
    }
  }

  const reviewedTexts = useMemo(() => new Set((sample?.reviewed_redactions || []).map(r => r.text.trimEnd())), [sample]);
  const matchesReviewed = phase === "redacted" && reviewedTexts.has(text.trimEnd());
  const own = ownText !== null && sample === null;
  // The reading the fields and codes come from: the model's, or the rules engine's when the model did not read the note.
  const rulesPrimary = result?.primary === "rules";
  const shownSide = result ? (rulesPrimary ? result.rules : result.llm) : null;
  const sections = useMemo(
    () => (config && shownSide?.proposal ? buildSections(config.profile, shownSide.proposal, rulesPrimary ? {} : result?.rules_agreement) : []),
    [config, result, shownSide, rulesPrimary],
  );
  const counts = useMemo(() => countStates(sections), [sections]);
  const confirmed = useMemo(() => countRules(sections), [sections]);
  const mentions = useMemo(() => mentionsView(shownSide?.unresolved_mentions || [], text), [shownSide, text]);
  const reviewCounts = useMemo(() => countReview(review, sections), [review, sections]);
  const recordChanged = changesRecord(review);
  const reviewStarted = reviewCounts.reviewed + reviewCounts.added + reviewCounts.rowsRemoved > 0;
  const codes = reviewedCodes ?? result?.codes ?? null;
  const tooLong = !!config && draft.length > config.max_text_chars;
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
          <span>Registry extraction demo · {config?.live_extraction.enabled ? "bundled samples and tester notes" : "synthetic notes only"}</span>
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
          <h2><span className="num">1</span> Choose a note</h2>
          <div className="tabs source-tabs" role="tablist" aria-label="Note source">
            <button role="tab" aria-selected={source === "samples"} className={source === "samples" ? "tab active" : "tab"} onClick={() => setSource("samples")}>
              Bundled samples
            </button>
            <button role="tab" aria-selected={source === "own"} className={source === "own" ? "tab active" : "tab"} onClick={() => setSource("own")}>
              Your own note
            </button>
          </div>
          {source === "samples" && (
            <div className="samples">
              {(config?.samples || []).map(s => (
                <button key={s.id} className={"sample" + (sample?.id === s.id ? " selected" : "")} onClick={() => void choose(s.id)}>
                  <strong>{s.title}</strong>
                  <small>{s.teaching_point}</small>
                  {!s.has_result && <small className="pending">Result not yet generated</small>}
                </button>
              ))}
            </div>
          )}
          {source === "own" && config && !config.live_extraction.enabled && (
            <p className="subtle">Tester access is not switched on on this server. The bundled samples are open to everyone.</p>
          )}
          {source === "own" && config?.live_extraction.enabled && !access && (
            <form
              className="own-note unlock"
              onSubmit={e => {
                e.preventDefault();
                void submitCode();
              }}
            >
              <p className="subtle">Using your own note needs a tester password. Ask the project owner for one.</p>
              <div className="row">
                <label>
                  Tester password
                  <input type="password" value={codeInput} onChange={e => setCodeInput(e.target.value)} autoComplete="off" />
                </label>
                <button className="primary" type="submit" disabled={!codeInput.trim()}>Unlock</button>
              </div>
              {unlockError && <p className="editor-problem" role="alert">{unlockError}</p>}
            </form>
          )}
          {source === "own" && config?.live_extraction.enabled && access && (
            <div className="own-note">
              <fieldset className="kind">
                <legend>What is this note?</legend>
                <label className="check">
                  <input type="radio" name="kind" checked={noteKind === "synthetic"} onChange={() => { setNoteKind("synthetic"); setAttested(false); }} />
                  Synthetic note (no real patient)
                </label>
                <label className="check">
                  <input type="radio" name="kind" checked={noteKind === "real_redacted"} onChange={() => { setNoteKind("real_redacted"); setAttested(false); }} />
                  Real note, to be redacted here before it is sent
                </label>
              </fieldset>
              <p className="subtle" role="note">
                {!access.model_configured
                  ? "The model reader is not set up on this server, so notes are read by the rules engine only."
                  : noteKind === "synthetic"
                    ? `After redaction the text is sent to ${access.provider} and read by ${access.model}. A reading usually takes about a minute.`
                    : access.real_notes_to_model
                      ? `After redaction the text is sent to ${access.provider} and read by ${access.model}. Redaction is automatic and can miss identifiers: read the redacted text before you extract.`
                      : "Real redacted notes are not approved for the model on this server. The redacted text is read by the rules engine on this server only and is sent nowhere else."}
                {" "}Nothing you enter is stored.
              </p>
              <label>
                Note text
                <textarea
                  rows={9}
                  value={draft}
                  onChange={e => setDraft(e.target.value)}
                  placeholder="Paste or type a robotic bronchoscopy or linear EBUS procedure note."
                  spellCheck={false}
                />
              </label>
              <div className="row">
                <button className="primary" disabled={!draft.trim() || tooLong} onClick={useOwnNote}>Use this note</button>
                <span className={tooLong ? "editor-problem" : "subtle"}>
                  {draft.length.toLocaleString()} of {config.max_text_chars.toLocaleString()} characters
                </span>
              </div>
            </div>
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
                {phase === "redacted" && own && <button onClick={() => resetReview(ownText || "")}>Start over</button>}
                {own && (phase === "reviewing" || phase === "redacted") && (
                  <button disabled={!selection} onClick={redactSelection} title="Select text in the note below that the scan missed, then press this.">
                    Redact selected text
                  </button>
                )}
                {sample && sample.reviewed_redactions.length > 0 && !matchesReviewed && (
                  <button className="link" onClick={useReviewed}>Use the reviewed redaction</button>
                )}
              </div>
              {status && <p className="status-line" role="status">{status}</p>}
              {phase === "reviewing" && (
                <ul className="detections" aria-label="Detected identifiers">
                  {detections.length === 0 && <li className="subtle">Nothing was detected. Apply to confirm the text as it is.</li>}
                  {own && <li className="subtle">Missed something? Select it in the note below and press &ldquo;Redact selected text&rdquo;.</li>}
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
            <NoteView text={text} spans={noteSpans} focus={focus} onSelect={own ? setSelection : undefined} />
          </section>

          <section>
            <section className="step">
              <h2><span className="num">3</span> Extract registry fields</h2>
              {own && ready && (
                <label className="check attest">
                  <input type="checkbox" checked={attested} onChange={e => setAttested(e.target.checked)} />
                  {ATTESTATION[noteKind]}
                </label>
              )}
              <div className="row">
                <button className="primary" disabled={!ready || busy || (own && !attested)} onClick={() => void runExtract()}>
                  {busy ? "Extracting…" : "Extract"}
                </button>
                {!ready && <span className="subtle">Apply redactions first.</span>}
                {busy && own && (
                  <span className="subtle" role="status">Reading the note… {elapsed}s. A model reading usually takes about a minute.</span>
                )}
              </div>
            </section>
            {result && (
              <>
                <p className="result-meta">
                  <span className="chip proposed">{result.source_label}</span>{" "}
                  {rulesPrimary
                    ? "Rules engine reading"
                    : inference.model ? `${inference.model}${inference.effort ? " · " + inference.effort + " effort" : ""}` : "No model result stored"}
                  {result.generated_at ? ` · generated ${result.generated_at.slice(0, 10)}` : ""}
                  {result.llm?.status && result.llm.status !== "proposed" ? ` · ${result.llm.status}` : ""}
                </p>
                {result.reader?.message && <p className="notice" role="note">{result.reader.message}</p>}
                {!result.llm?.proposal && !result.reader && (
                  <p className="notice" role="note">
                    No model result is stored for this sample yet. Shown here is the rules-engine reading.
                  </p>
                )}
                {shownSide?.proposal && (
                  <p className="review-bar" role="status">
                    <strong>Your review:</strong>{" "}
                    {reviewStarted ? (
                      <>
                        {reviewCounts.reviewed} of {reviewCounts.total} values checked ({reviewCounts.confirmed} confirmed, {reviewCounts.corrected} corrected,{" "}
                        {reviewCounts.removed} removed)
                        {reviewCounts.added > 0 && <> · {reviewCounts.added} added</>}
                        {reviewCounts.rowsRemoved > 0 && <> · {reviewCounts.rowsRemoved} row{reviewCounts.rowsRemoved === 1 ? "" : "s"} removed</>}
                        {" · "}
                        <button className="link" onClick={clearFindingsReview}>Clear review</button>
                      </>
                    ) : (
                      <>confirm each value, correct it, or remove it. Blank fields can be filled in.</>
                    )}
                    <br />
                    <span className="subtle">Your review stays in this browser tab. Nothing is saved.</span>
                  </p>
                )}
                {summary && result.llm?.proposal && (
                  <p className="tally">
                    <strong>{counts.value + counts.negative}</strong> values with a supporting passage
                    {counts.stated_missing > 0 && <> · <strong>{counts.stated_missing}</strong> stated as unknown or not done</>}
                    {counts.conflict > 0 && <> · <strong>{counts.conflict}</strong> unclear</>}
                    <br />
                    Side by side, the LLM filled <strong>{summary.llm_total}</strong> fields and the rules engine <strong>{summary.rules_total}</strong>.
                    {confirmed.agree + confirmed.differ > 0 && (
                      <>
                        <br />
                        <span className="rules-mark">✓ rules</span> marks the <strong>{confirmed.agree}</strong> values shown here that the rules
                        engine extracted identically on its own
                        {confirmed.differ > 0 && <>; it read <strong>{confirmed.differ}</strong> differently, shown beside the value</>}.
                        Agreement between two methods is a reason for more confidence, not proof. An unmarked value is one the rules
                        engine did not extract.
                      </>
                    )}
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
                  shownSide?.proposal ? (
                    <>
                      <FieldList sections={sections} text={text} onFocus={setFocus} review={review} onReview={changeReview} />
                      {mentions.length > 0 && (
                        <section>
                          <h3>Set aside, not recorded</h3>
                          <p className="subtle">
                            Planned, historical, uncertain or unmappable statements are listed here and never turned into values.
                          </p>
                          <ul className="unresolved">
                            {mentions.map((m, i) => (
                              <li key={i} title={m.notes.join("\n")}>
                                <strong>{m.label}</strong>
                                {m.quote ? <>: &ldquo;{m.quote}&rdquo; </> : <> {m.notes[0]} </>}
                                {m.span && <button className="link" onClick={() => setFocus(m.span)}>show in note</button>}
                              </li>
                            ))}
                          </ul>
                        </section>
                      )}
                    </>
                  ) : (
                    <p className="subtle">Nothing was extracted from this note.</p>
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
                {tab === "codes" && (
                  <>
                    {recordChanged && !reviewedCodes && (
                      <p className="notice" role="note">
                        These codes come from the extraction as it was returned, before your corrections.{" "}
                        <button className="mini primary" disabled={recoding} onClick={() => void updateCodes()}>
                          {recoding ? "Updating…" : "Update codes with my corrections"}
                        </button>
                      </p>
                    )}
                    {reviewedCodes && <p className="status-line" role="status">Codes updated from your corrected record.</p>}
                    {codesError && <p className="editor-problem" role="alert">{codesError}</p>}
                    {codes ? <CodesCard codes={codes} text={text} onFocus={setFocus} /> : <p className="subtle">No codes without an extraction.</p>}
                  </>
                )}
              </>
            )}
          </section>
        </div>
      </main>
      <footer>
        Software prototype for demonstration; outputs require clinician and coder review. Bundled samples are synthetic. Tester notes
        and reviews are not stored.
      </footer>
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
