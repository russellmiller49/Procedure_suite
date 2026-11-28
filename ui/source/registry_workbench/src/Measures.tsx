import {label} from "./review";

export type Analysis = {
  tables: Record<string, unknown[]>;
  measures: {
    counts: Record<string, number>;
    strict_index_yield: {numerator: number; denominator: number; rate: number | null};
    definitions: Record<string, string>;
    adjustment: string;
  };
};

const GROUPS: [string, RegExp][] = [
  ["Cases and components", /^(cases|robotic|linear)_/],
  ["Navigation and targets", /^(navigation|peripheral|targets)_/],
  ["Sampling, specimens and nodes", /^(acquisition|acquisitions|aggregate|reported|nodal|specimens)_/],
  ["Index results", /^(index|strict|later)_/],
  ["Safety", /^(safety|days)_/],
];

function group(key: string): string {
  return GROUPS.find(([, re]) => re.test(key))?.[0] || "Other";
}

export function Measures({analysis}: {analysis: Analysis}) {
  const {counts, strict_index_yield: yieldMeasure, definitions} = analysis.measures;
  const grouped: Record<string, [string, number][]> = Object.fromEntries([...GROUPS.map(([name]) => [name, []]), ["Other", []]]);
  for (const [key, value] of Object.entries(counts).sort()) grouped[group(key)].push([key, value]);
  return (
    <div className="measures">
      <p className="subtle">
        Approved revisions with no approval errors only · {analysis.measures.adjustment} · engineering, not clinical validation.
      </p>
      <table className="summary">
        <tbody>
          <tr><th>Approved cases</th><td>{analysis.tables.cases?.length ?? 0}</td></tr>
          <tr>
            <th>Strict index yield</th>
            <td>
              {yieldMeasure.numerator} / {yieldMeasure.denominator}
              {yieldMeasure.rate == null ? " (no attempted peripheral targets)" : ` (${(yieldMeasure.rate * 100).toFixed(1)}%)`}
            </td>
          </tr>
        </tbody>
      </table>
      {Object.entries(grouped).filter(([, rows]) => rows.length).map(([name, rows]) => (
        <details key={name} open={name !== "Safety"}>
          <summary>{name}</summary>
          <table>
            <tbody>
              {rows.map(([key, value]) => (
                <tr key={key}><td>{label(key)}</td><td className="num">{value}</td></tr>
              ))}
            </tbody>
          </table>
        </details>
      ))}
      <details>
        <summary>Definitions</summary>
        <dl>
          {Object.entries(definitions).map(([key, text]) => (
            <div key={key}><dt>{label(key)}</dt><dd>{text}</dd></div>
          ))}
        </dl>
      </details>
      <details>
        <summary>Normalized tables</summary>
        <table>
          <tbody>
            {Object.entries(analysis.tables).map(([name, rows]) => (
              <tr key={name}><td>{label(name)}</td><td className="num">{rows.length} rows</td></tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
