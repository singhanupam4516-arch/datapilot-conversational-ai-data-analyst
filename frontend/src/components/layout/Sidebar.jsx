import { BarChartIcon, DatabaseIcon, MessageSquareIcon, UploadIcon } from "../../icons/Icons";

const STEPS = [
  { key: "upload", label: "Upload", Icon: UploadIcon },
  { key: "dashboard", label: "Analyze", Icon: BarChartIcon },
  { key: "chat", label: "Chat", Icon: MessageSquareIcon },
];

export function Sidebar({ session, activeView, onNavigate, onReset }) {
  return (
    <aside className="sidebar">
      <button onClick={onReset} className="sidebar-brand">
        <span className="sidebar-brand-icon">
          <DatabaseIcon size={16} className="text-accent-data" style={{ color: "var(--color-accent-data)" }} />
        </span>
        <span className="sidebar-brand-name">DataPilot</span>
      </button>
      <p className="sidebar-tagline">Conversational AI Data Analyst</p>

      <nav className="sidebar-nav">
        {STEPS.map(({ key, label, Icon }) => {
          const isDisabled = key !== "upload" && !session;
          const isActive = activeView === key;
          return (
            <button
              key={key}
              disabled={isDisabled}
              onClick={() => onNavigate(key)}
              className={`nav-item${isActive ? " active" : ""}`}
            >
              <Icon size={16} className="nav-icon" style={isActive ? { color: "var(--color-accent-data)" } : undefined} />
              {label}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        {session ? (
          <>
            <p className="sidebar-footer-label">Active dataset</p>
            <p className="sidebar-footer-filename" title={session.filename}>
              {session.filename}
            </p>
            <p className="sidebar-footer-meta">
              {session.row_count.toLocaleString()} rows &middot; {session.column_count} columns
            </p>
          </>
        ) : (
          <p className="sidebar-footer-label">No dataset loaded yet.</p>
        )}
      </div>
    </aside>
  );
}
