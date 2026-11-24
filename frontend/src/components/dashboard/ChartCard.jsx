export function ChartCard({ title, imageBase64 }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h4>{title}</h4>
      </div>
      <div className="chart-card-body">
        <img src={`data:image/png;base64,${imageBase64}`} alt={`Chart: ${title}`} />
      </div>
    </div>
  );
}
