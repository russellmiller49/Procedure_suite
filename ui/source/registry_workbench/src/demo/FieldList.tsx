import {useState} from "react";
import {label} from "../review";
import {fieldLabel, STATE_LABEL, verifiedSpan, type FieldInput, type FieldView, type RowView, type SectionView} from "./fields";
import {confirmRow, decide, isRecorded, parseInput, reviewedDisplay, toggleRow, type Decision, type Review} from "./reviewState";

type Props = {
  sections: SectionView[];
  text: string;
  onFocus: (span: [number, number]) => void;
  review: Review;
  onReview: (next: Review) => void;
};

/** One input for one contract value: a list for coded fields, a number or text box otherwise. */
function ValueEditor({field, initial, onSave, onCancel}: {field: FieldView; initial: unknown; onSave: (value: unknown) => void; onCancel: () => void}) {
  const input: FieldInput = field.input;
  const [raw, setRaw] = useState(initial == null ? "" : String(initial));
  const [problem, setProblem] = useState("");
  const name = fieldLabel(field.name, field.units);
  const choices: [string, string][] | null =
    input.kind === "enum" ? input.options.map(option => [option, label(option)] as [string, string])
    : input.kind === "boolean" ? [["true", "Yes"], ["false", "No"]]
    : null;
  const save = () => {
    const parsed = parseInput(input, raw);
    if (parsed.ok) onSave(parsed.value);
    else setProblem(parsed.message);
  };
  return (
    <form
      className="editor"
      onSubmit={e => {
        e.preventDefault();
        save();
      }}
    >
      {choices ? (
        <select aria-label={name} value={raw} onChange={e => setRaw(e.target.value)} autoFocus>
          <option value="">Choose…</option>
          {choices.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
        </select>
      ) : (
        <input
          aria-label={name}
          type={input.kind === "text" ? "text" : "number"}
          step={input.kind === "number" ? "any" : undefined}
          value={raw}
          onChange={e => setRaw(e.target.value)}
          autoFocus
        />
      )}
      {field.units && <span className="units">{field.units}</span>}
      <button type="submit" className="mini primary">Save</button>
      <button type="button" className="mini" onClick={onCancel}>Cancel</button>
      {problem && <span className="editor-problem" role="alert">{problem}</span>}
    </form>
  );
}

function Field({field, text, onFocus, decision, onDecide}: {
  field: FieldView;
  text: string;
  onFocus: Props["onFocus"];
  decision: Decision | undefined;
  onDecide: (decision: Decision | null) => void;
}) {
  const [editing, setEditing] = useState(false);
  const span = verifiedSpan(text, field.span, field.quote);
  const name = fieldLabel(field.name, field.units);
  const shown = reviewedDisplay(field, decision);
  const status = decision?.status;
  const removed = status === "removed";
  const changed = status === "corrected" || status === "added";
  const current = changed ? (decision as {value: unknown}).value : field.value;
  // An unresolved field has no value to confirm: the reviewer sets one or removes it.
  const canConfirm = field.state === "value" || field.state === "negative" || field.state === "stated_missing";
  return (
    <div className={"fact " + shown.state + (status ? " reviewed " + status : "")}>
      <dt title={field.definition}>{name}</dt>
      <dd>
        {!changed && STATE_LABEL[field.state] && <span className="state">{STATE_LABEL[field.state]} </span>}
        <strong className={removed ? "struck" : undefined}>{shown.display}</strong>
        {field.units && shown.state === "value" ? <span className="units"> {field.units}</span> : null}
        {span ? (
          <button className="link quote" onClick={() => onFocus(span)} title={field.quote}>show in note</button>
        ) : field.derived && !changed ? (
          <span className="provenance-tag"> derived</span>
        ) : null}
        {!status && field.rules?.state === "agree" && (
          <span className="rules-mark" title="The rules engine extracted the same value on its own.">✓ rules</span>
        )}
        {!status && field.rules?.state === "differ" && (
          <span className="rules-differ" title="The rules engine extracted a different value for this field.">
            Rules engine read: {field.rules.display}
          </span>
        )}
        {status === "confirmed" && <span className="review-tag ok">Confirmed</span>}
        {status === "corrected" && (
          <span className="review-tag edit">Corrected{field.display ? <> · was {field.display}</> : null}</span>
        )}
        {status === "added" && <span className="review-tag edit">Added by you</span>}
        {removed && <span className="review-tag gone">Removed</span>}
        {editing ? (
          <ValueEditor
            field={field}
            initial={current}
            onCancel={() => setEditing(false)}
            onSave={value => {
              onDecide({status: field.state === "not_extracted" ? "added" : "corrected", value});
              setEditing(false);
            }}
          />
        ) : (
          <span className="review-actions">
            {!status && canConfirm && (
              <button className="mini" onClick={() => onDecide({status: "confirmed"})} aria-label={`Confirm ${name}`}>Confirm</button>
            )}
            {!removed && (
              <button className="mini" onClick={() => setEditing(true)} aria-label={`Correct ${name}`}>
                {field.state === "conflict" && !changed ? "Set value" : changed ? "Edit" : "Correct"}
              </button>
            )}
            {!status && (
              <button className="mini" onClick={() => onDecide({status: "removed"})} aria-label={`Remove ${name}`}>Remove</button>
            )}
            {status && <button className="mini" onClick={() => onDecide(null)} aria-label={`Undo review of ${name}`}>Undo</button>}
          </span>
        )}
      </dd>
    </div>
  );
}

/** A field the extractor left blank: the reviewer can add a value they read in the note. */
function BlankField({field, onDecide}: {field: FieldView; onDecide: (decision: Decision) => void}) {
  const [editing, setEditing] = useState(false);
  const name = fieldLabel(field.name, field.units);
  if (!editing) {
    return <button className="mini add" onClick={() => setEditing(true)} title={field.definition} aria-label={`Add ${name}`}>+ {name}</button>;
  }
  return (
    <span className="blank-editor">
      <span className="blank-name">{name}</span>
      <ValueEditor field={field} initial={null} onCancel={() => setEditing(false)} onSave={value => onDecide({status: "added", value})} />
    </span>
  );
}

function Row({row, text, onFocus, review, onReview}: {row: RowView} & Omit<Props, "sections">) {
  const removed = review.removedRows.includes(row.key);
  const added = (f: FieldView) => review.decisions[f.path]?.status === "added";
  const shown = row.fields.filter(f => f.state !== "not_extracted" || added(f));
  const blank = row.fields.filter(f => f.state === "not_extracted" && !added(f));
  const open = row.fields.filter(f => isRecorded(f) && f.state !== "conflict" && !review.decisions[f.path]).length;
  // Only a row of a list can be removed; the case block and the overall line are single values.
  const removable = /^\/[a-z_]+\/\d+$/.test(row.key);
  if (removed) {
    return (
      <article className="fact-row removed-row">
        <div className="row-head">
          <h4 className="struck">{row.title}</h4>
          <span>
            <span className="review-tag gone">Row removed</span>{" "}
            <button className="mini" onClick={() => onReview(toggleRow(review, row.key))}>Undo</button>
          </span>
        </div>
      </article>
    );
  }
  return (
    <article className="fact-row">
      <div className="row-head">
        <h4>{row.title}</h4>
        <span className="row-actions">
          {open > 0 && <button className="mini" onClick={() => onReview(confirmRow(review, row))}>Confirm all {open}</button>}
          {removable && <button className="mini" onClick={() => onReview(toggleRow(review, row.key))}>Remove row</button>}
        </span>
      </div>
      <dl className="facts">
        {shown.map(f => (
          <Field
            key={f.path}
            field={f}
            text={text}
            onFocus={onFocus}
            decision={review.decisions[f.path]}
            onDecide={decision => onReview(decide(review, f.path, decision))}
          />
        ))}
      </dl>
      {blank.length > 0 && (
        <details className="blank">
          <summary>Not extracted ({blank.length})</summary>
          <p className="subtle">
            The extractor returned nothing for these fields. That is not a statement about what the note says. Pick one to
            add a value you read in the note.
          </p>
          <p className="blank-list">
            {blank.map(f => <BlankField key={f.path} field={f} onDecide={decision => onReview(decide(review, f.path, decision))} />)}
          </p>
        </details>
      )}
    </article>
  );
}

/** Registry fields with the reviewer's confirm, correct and remove controls. A blank is "Not extracted". */
export function FieldList({sections, text, onFocus, review, onReview}: Props) {
  return (
    <div className="field-list">
      {sections.filter(s => s.rows.length > 0).map(section => (
        <section key={section.collection}>
          <h3>{section.title}</h3>
          {section.rows.map(row => <Row key={row.key} row={row} text={text} onFocus={onFocus} review={review} onReview={onReview} />)}
        </section>
      ))}
    </div>
  );
}
