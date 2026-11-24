function isRecordArray(value) {
  return Array.isArray(value);
}

function isPlainObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function formatCell(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
  return String(value);
}

/** Renders whatever shape the executed Pandas code returned: a scalar, a
 * dict (Series -> key/value rows), or a list of records (DataFrame rows). */
export function ResultCard({ result }) {
  if (result === null || result === undefined) {
    return <p className="result-empty">No return value — check the chart above, if any.</p>;
  }

  if (isRecordArray(result)) {
    if (result.length === 0) return <p className="result-empty">Empty result.</p>;
    const columns = Object.keys(result[0]);
    return (
      <div className="result-table-wrapper">
        <table className="result-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.slice(0, 20).map((row, index) => (
              <tr key={index}>
                {columns.map((col) => (
                  <td key={col}>{formatCell(row[col])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {result.length > 20 && <p className="result-table-note">Showing 20 of {result.length} rows.</p>}
      </div>
    );
  }

  if (isPlainObject(result)) {
    const entries = Object.entries(result);
    return (
      <div className="result-kv-list">
        {entries.slice(0, 20).map(([key, value]) => (
          <div key={key} className="result-kv-row">
            <span className="kv-key">{key}</span>
            <span className="kv-value">{formatCell(value)}</span>
          </div>
        ))}
      </div>
    );
  }

  return <div className="result-scalar">{formatCell(result)}</div>;
}
