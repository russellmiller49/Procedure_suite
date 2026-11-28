import type {CodeEvidence, Codes} from "./demoApi";
import {verifiedSpan} from "./fields";

type Props = {codes: Codes; text: string; onFocus: (span: [number, number]) => void};

function Passage({item, text, onFocus}: {item: CodeEvidence; text: string; onFocus: Props["onFocus"]}) {
  const span = item.start != null && item.end != null ? verifiedSpan(text, [item.start, item.end], item.quote) : null;
  return (
    <li>
      {span ? <button className="link" onClick={() => onFocus(span)} title={item.quote}>{item.label}</button> : item.label}
      {item.reason ? <span className="subtle">: {item.reason}</span> : null}
    </li>
  );
}

/** Codes proposed by the existing coding rules from the extracted facts, each with its passages. */
export function CodesCard({codes, text, onFocus}: Props) {
  const general = codes.review_flags.filter(f => f.codes.length === 0);
  return (
    <div className="codes">
      <p className="subtle">{codes.scope_note}</p>
      {codes.codes.length === 0 && <p>No code in this family is suggested from the extracted facts.</p>}
      {codes.codes.map(code => (
        <article key={code.code} className={"code" + (code.needs_review ? " review" : "")}>
          <div className="row-head">
            <h4>
              {code.role === "add_on" ? "+" : ""}{code.code}
              {code.modifiers.length > 0 && <span className="chip">modifier {code.modifiers.join(", ")}</span>}
              {(code.units ?? 1) > 1 && <span className="chip">{code.units} units</span>}
            </h4>
            {code.needs_review && <span className="chip degraded">needs coding review</span>}
          </div>
          <p>{code.description}</p>
          {code.evidence.length > 0 && (
            <>
              <h5>Counted</h5>
              <ul className="passages">{code.evidence.map((e, i) => <Passage key={i} item={e} text={text} onFocus={onFocus} />)}</ul>
            </>
          )}
          {code.excluded.length > 0 && (
            <>
              <h5>Not counted</h5>
              <ul className="passages">{code.excluded.map((e, i) => <Passage key={i} item={e} text={text} onFocus={onFocus} />)}</ul>
            </>
          )}
          {code.review_flags.map((flag, i) => <p key={i} className="field-alert">{flag}</p>)}
        </article>
      ))}
      {codes.dropped.length > 0 && (
        <details>
          <summary>Considered and not suggested ({codes.dropped.length})</summary>
          <ul>{codes.dropped.map(d => <li key={d.code}><strong>{d.code}</strong> {d.reason}</li>)}</ul>
        </details>
      )}
      {general.length > 0 && (
        <div className="notice" role="note">
          {general.map((f, i) => <p key={i}>{f.message}</p>)}
        </div>
      )}
      <details>
        <summary>Not assessed here</summary>
        <ul>{codes.not_assessed.map(n => <li key={n.label}><strong>{n.codes.join(", ")}</strong> {n.label}: {n.reason}.</li>)}</ul>
      </details>
    </div>
  );
}
