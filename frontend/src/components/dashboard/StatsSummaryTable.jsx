function formatNumber(value) {
  return Number.isInteger(value)
    ? value.toLocaleString()
    : value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export function StatsSummaryTable({ numericSummary, categoricalSummary }) {
  const numericColumns = Object.entries(numericSummary);
  const categoricalColumns = Object.entries(categoricalSummary);

  return (
    <div className="stats-grid">
      {numericColumns.length > 0 && (
        <div className="panel">
          <div className="panel-header">
            <h3>Numeric columns</h3>
          </div>
          <div className="stats-table-wrapper">
            <table className="stats-table">
              <thead>
                <tr>
                  <th>Column</th>
                  <th>Mean</th>
                  <th>Median</th>
                  <th>Std</th>
                  <th>Min</th>
                  <th>Max</th>
                </tr>
              </thead>
              <tbody>
                {numericColumns.map(([column, stats]) => (
                  <tr key={column}>
                    <td>{column}</td>
                    <td className="cell-mean">{formatNumber(stats.mean)}</td>
                    <td>{formatNumber(stats.median)}</td>
                    <td className="cell-muted">{formatNumber(stats.std)}</td>
                    <td className="cell-muted">{formatNumber(stats.min)}</td>
                    <td className="cell-muted">{formatNumber(stats.max)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {categoricalColumns.length > 0 && (
        <div className="panel">
          <div className="panel-header">
            <h3>Categorical columns</h3>
          </div>
          <div className="categorical-list">
            {categoricalColumns.map(([column, stats]) => (
              <div key={column} className="categorical-row">
                <div className="categorical-row-header">
                  <span className="column-name">{column}</span>
                  <span className="unique-count">{stats.unique_count} unique</span>
                </div>
                <div className="tag-list">
                  {Object.entries(stats.top_values).map(([value, count]) => (
                    <span key={value} className="tag">
                      {value} <span className="tag-count">{count}</span>
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
