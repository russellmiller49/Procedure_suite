import {useState} from "react";
import {label} from "./review";

export type Comparison = {
  sources: string[];
  rows: {collection: string; row: string; field: string; values: Record<string, unknown>; agree: boolean}[];
};

const show = (v: unknown) => (v == null ? "—" : typeof v === "boolean" ? (v ? "yes" : "no") : String(v));

export function Compare({comparison}: {comparison: Comparison}) {
  const [onlyDifferences, setOnlyDifferences] = useState(true);
  const rows = comparison.rows.filter(r => !onlyDifferences || !r.agree);
  const differences = comparison.rows.filter(r => !r.agree).length;
  return (
    <div className="compare">
      <div className="row">
        <strong>{differences} of {comparison.rows.length} values differ</strong>
        <label className="check">
          <input type="checkbox" checked={onlyDifferences} onChange={e => setOnlyDifferences(e.target.checked)} />
          Only show differences
        </label>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Section</th>
              <th>Row</th>
              <th>Field</th>
              {comparison.sources.map(s => <th key={s}>{s}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={`${r.collection}|${r.row}|${r.field}`} className={r.agree ? "" : "differs"}>
                <td>{label(r.collection)}</td>
                <td>{r.row}</td>
                <td>{label(r.field)}</td>
                {comparison.sources.map(s => <td key={s}>{show(r.values[s])}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
