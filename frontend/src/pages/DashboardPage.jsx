import { useEffect, useState } from "react";
import { BarChartIcon, LoaderIcon, MessageSquareIcon } from "../icons/Icons";
import { StatsSummaryTable } from "../components/dashboard/StatsSummaryTable";
import { ChartCard } from "../components/dashboard/ChartCard";
import { api, ApiError } from "../api/client";

export function DashboardPage({ session, onGoToChat }) {
  const [eda, setEda] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setEda(null);
    setErrorMessage(null);

    api
      .getEda(session.session_id)
      .then((result) => {
        if (!cancelled) setEda(result);
      })
      .catch((error) => {
        if (!cancelled) setErrorMessage(error instanceof ApiError ? error.message : "Could not load analysis.");
      });

    return () => {
      cancelled = true;
    };
  }, [session.session_id]);

  if (errorMessage) {
    return <p className="chat-error" style={{ padding: "2rem" }}>{errorMessage}</p>;
  }

  if (!eda) {
    return (
      <div className="chat-status" style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "2rem" }}>
        <LoaderIcon size={16} className="spin" />
        Running automated EDA — statistical profiling, distributions, and correlations…
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">
            <BarChartIcon size={22} style={{ color: "var(--color-accent-data)" }} />
            Automated EDA
          </h1>
          <p className="dashboard-subtitle">
            {session.filename} &middot; {session.row_count.toLocaleString()} rows &middot; {session.column_count}{" "}
            columns
          </p>
        </div>
        <button onClick={onGoToChat} className="btn btn-insight">
          <MessageSquareIcon size={15} />
          Chat with this data
        </button>
      </div>

      <StatsSummaryTable numericSummary={eda.numeric_summary} categoricalSummary={eda.categorical_summary} />

      {eda.distribution_charts.length > 0 && (
        <div>
          <h2 className="section-label">Distributions</h2>
          <div className="chart-grid">
            {eda.distribution_charts.map((chart) => (
              <ChartCard key={chart.column} title={chart.column} imageBase64={chart.image_base64} />
            ))}
          </div>
        </div>
      )}

      {eda.correlation_heatmap && (
        <div>
          <h2 className="section-label">Correlation</h2>
          <div className="heatmap-wrapper">
            <ChartCard title="Correlation heatmap" imageBase64={eda.correlation_heatmap} />
          </div>
        </div>
      )}
    </div>
  );
}
