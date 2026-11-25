import {fieldLabel, STATE_LABEL, verifiedSpan, type FieldView, type SectionView} from "./fields";

type Props = {sections: SectionView[]; text: string; onFocus: (span: [number, number]) => void};

function Field({field, text, onFocus}: {field: FieldView; text: string; onFocus: Props["onFocus"]}) {
  const span = verifiedSpan(text, field.span, field.quote);
  return (
    <div className={"fact " + field.state}>
      <dt title={field.definition}>{fieldLabel(field.name, field.units)}</dt>
      <dd>
        {STATE_LABEL[field.state] && <span className="state">{STATE_LABEL[field.state]} </span>}
        <strong>{field.display}</strong>
        {field.units && field.state === "value" ? <span className="units"> {field.units}</span> : null}
        {span ? (
          <button className="link quote" onClick={() => onFocus(span)} title={field.quote}>show in note</button>
        ) : field.derived ? (
          <span className="provenance-tag"> derived</span>
        ) : null}
        {field.rules?.state === "agree" && (
          <span className="rules-mark" title="The rules engine extracted the same value on its own.">✓ rules</span>
        )}
        {field.rules?.state === "differ" && (
          <span className="rules-differ" title="The rules engine extracted a different value for this field.">
            Rules engine read: {field.rules.display}
          </span>
        )}
      </dd>
    </div>
  );
}

/** Read-only registry fields. A blank is "Not extracted": it says nothing about the note. */
export function FieldList({sections, text, onFocus}: Props) {
  return (
    <div className="field-list">
      {sections.filter(s => s.rows.length > 0).map(section => (
        <section key={section.collection}>
          <h3>{section.title}</h3>
          {section.rows.map(row => {
            const shown = row.fields.filter(f => f.state !== "not_extracted");
            const blank = row.fields.filter(f => f.state === "not_extracted");
            return (
              <article key={row.key} className="fact-row">
                <h4>{row.title}</h4>
                <dl className="facts">
                  {shown.map(f => <Field key={f.path} field={f} text={text} onFocus={onFocus} />)}
                </dl>
                {blank.length > 0 && (
                  <details className="blank">
                    <summary>Not extracted ({blank.length})</summary>
                    <p className="subtle">
                      The extractor returned nothing for these fields. That is not a statement about what the note says.
                    </p>
                    <p>{blank.map(f => fieldLabel(f.name, f.units)).join(" · ")}</p>
                  </details>
                )}
              </article>
            );
          })}
        </section>
      ))}
    </div>
  );
}
