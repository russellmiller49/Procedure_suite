import type {Profile, Schema, Span, Values} from "./types";
import {KEYS, MISSING, REFERENCES, label, provenanceFor} from "./review";

type Props = {
  profile: Profile;
  values: Values;
  onChange: (values: Values) => void;
  onEvidence?: (span: Span) => void;
  disabled?: boolean;
};

/** Schema-driven review form for the robotic_ebus_v1 launch contract (ported from the clinical app). */
export function LaunchReview({profile, values, onChange, onEvidence, disabled = false}: Props) {
  const schema = profile.schema;
  function resolve(s: Schema): Schema {
    if (s.$ref) return resolve(schema.$defs[s.$ref.split("/").at(-1)]);
    if (s.anyOf) return resolve(s.anyOf.find((x: Schema) => x.type !== "null") || {});
    return s;
  }
  function change(collection: string, index: number | undefined, field: string, value: any, reason = "not_documented") {
    const v = structuredClone(values);
    const path = `/${collection}${index == null ? "" : "/" + index}/${field}`;
    const row = index == null ? v[collection] : v[collection][index];
    row[field] = value;
    const prior = provenanceFor(v, path);
    v.field_provenance = (v.field_provenance || []).filter((p: Values) => p.field_path !== path);
    v.field_provenance.push({
      ...prior,
      field_path: path,
      value_origin: value == null ? "missing" : "manual",
      missingness_reason: value == null ? reason : null,
      conflict_status: "none",
      review_status: prior?.value_origin === "extracted" ? "amended" : "reviewed",
    });
    onChange(v);
  }
  function remove(collection: string, index: number) {
    const v = structuredClone(values);
    v[collection].splice(index, 1);
    v.field_provenance = (v.field_provenance || []).flatMap((p: Values) => {
      const parts = p.field_path.split("/");
      if (parts[1] !== collection) return [p];
      const n = Number(parts[2]);
      if (n === index) return [];
      if (n > index) {
        parts[2] = String(n - 1);
        return [{...p, field_path: parts.join("/")}];
      }
      return [p];
    });
    onChange(v);
  }
  function add(collection: string) {
    const row: Values = {};
    if (KEYS[collection]) row[KEYS[collection]] = crypto.randomUUID();
    if (collection === "procedures") {
      row.category = values.procedures.some((p: Values) => p.category === "robotic_bronchoscopy") ? "linear_ebus" : "robotic_bronchoscopy";
      row.performance = "not_documented";
    }
    if (collection === "follow_up") {
      row.window = values.follow_up.some((f: Values) => f.window === "days_0_7") ? "days_8_30" : "days_0_7";
      row.complete = false;
    }
    if (collection === "sampling_acquisitions") row.acquisition_record_granularity = "aggregate_reported";
    onChange({...values, [collection]: [...(values[collection] || []), row]});
  }

  function rowFields(collection: string, row: Values, index?: number) {
    const entity = resolve(index == null ? schema.properties[collection] : resolve(schema.properties[collection]).items);
    return (
      <div className="launch-fields">
        {Object.entries(entity.properties).map(([field, raw]) => {
          const property = resolve(raw as Schema);
          const value = row[field];
          const path = `/${collection}${index == null ? "" : "/" + index}/${field}`;
          if (field === KEYS[collection]) return <small className="row-identity" key={field}>{label(field)}: {value}</small>;
          const help = profile.help[`${collection}.${field}`] || {};
          const options = property.enum || (property.type === "boolean" ? [true, false] : null);
          const link = REFERENCES[field];
          const linked = link ? (values[link] || []).filter((r: Values) => r[KEYS[link]] !== row[KEYS[collection]]) : null;
          const provenance = provenanceFor(values, path);
          const conflict = provenance?.conflict_status === "unresolved";
          return (
            <div className={"launch-field" + (conflict ? " conflict" : "")} key={field}>
              <label title={help.definition}>
                {label(field)}
                {help.units ? <span className="units"> ({help.units})</span> : null}
                {linked ? (
                  <select disabled={disabled} value={value ?? ""} onChange={e => change(collection, index, field, e.target.value || null)}>
                    <option value="">Not linked</option>
                    {linked.map((r: Values, i: number) => (
                      <option key={r[KEYS[link]]} value={r[KEYS[link]]}>
                        {label(link)} {i + 1} · {r.specimen_label || r.iaslc_station || r.lobe || r.result_status || r.localization_modality || ""}
                      </option>
                    ))}
                  </select>
                ) : options ? (
                  <select
                    disabled={disabled}
                    value={value == null ? "" : String(value)}
                    onChange={e => change(collection, index, field, e.target.value === "" ? null : property.type === "boolean" ? e.target.value === "true" : e.target.value)}
                  >
                    <option value="">Not documented</option>
                    {options.map((o: any) => (
                      <option key={String(o)} value={String(o)}>{typeof o === "boolean" ? (o ? "Yes" : "No") : label(o)}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    disabled={disabled}
                    type={property.type === "integer" || property.type === "number" ? "number" : property.format === "date-time" ? "datetime-local" : "text"}
                    min={property.minimum}
                    max={property.maximum}
                    step={property.type === "integer" ? 1 : "any"}
                    maxLength={property.maxLength}
                    value={value ?? ""}
                    onChange={e => change(collection, index, field, e.target.value === "" ? null : ["number", "integer"].includes(property.type) ? Number(e.target.value) : e.target.value)}
                  />
                )}
              </label>
              {value == null && (
                <select
                  className="missing"
                  aria-label={label(field) + " missingness reason"}
                  disabled={disabled}
                  value={provenance?.missingness_reason || "not_documented"}
                  onChange={e => change(collection, index, field, null, e.target.value)}
                >
                  {MISSING.map(reason => <option key={reason} value={reason}>{label(reason)}</option>)}
                </select>
              )}
              {provenance?.source_excerpt && (
                <div className="field-evidence">
                  <button
                    type="button"
                    className="link"
                    onClick={() => onEvidence?.({document_id: provenance.source_document_id, start: provenance.source_start, end: provenance.source_end})}
                  >
                    “{provenance.source_excerpt.length > 70 ? provenance.source_excerpt.slice(0, 70) + "…" : provenance.source_excerpt}”
                  </button>
                  <span className="provenance-tag">{label(provenance.review_status || "proposed")}</span>
                </div>
              )}
              {conflict && (
                <p className="field-alert" role="alert">
                  Unresolved: the extractor claimed {provenance.raw_value}. Set the value or confirm it is missing.
                </p>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="launch-review">
      {Object.entries(profile.sections).map(([collection, title]) => (
        <details key={collection} open={["procedures", "targets", "station_surveys"].includes(collection)}>
          <summary>
            {title} {Array.isArray(values[collection]) ? <span className="count">{values[collection].length}</span> : null}
          </summary>
          {collection === "case_details"
            ? rowFields(collection, values.case_details || {})
            : (values[collection] || []).map((row: Values, i: number) => (
                <article key={row[KEYS[collection]] || i}>
                  <div className="row-head">
                    <h4>{title} {i + 1}</h4>
                    <button type="button" disabled={disabled} onClick={() => remove(collection, i)}>Remove</button>
                  </div>
                  {rowFields(collection, row, i)}
                </article>
              ))}
          {collection !== "case_details" && (
            <button
              type="button"
              disabled={disabled || (collection === "procedures" && values.procedures.length >= 2) || (collection === "follow_up" && values.follow_up.length >= 2)}
              onClick={() => add(collection)}
            >
              Add row
            </button>
          )}
        </details>
      ))}
    </div>
  );
}
