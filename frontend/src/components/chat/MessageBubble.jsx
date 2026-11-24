import { useState } from "react";
import { ChevronDownIcon, ChevronRightIcon, CodeIcon, SparklesIcon, UserIcon } from "../../icons/Icons";
import { ResultCard } from "./ResultCard";

export function MessageBubble({ message }) {
  const [showCode, setShowCode] = useState(false);

  return (
    <div className="message-group">
      <div className="message-row user">
        <div className="bubble user">
          <p style={{ margin: 0 }}>{message.question}</p>
        </div>
        <div className="avatar avatar-user">
          <UserIcon size={13} style={{ color: "var(--color-text-muted)" }} />
        </div>
      </div>

      <div className="message-row">
        <div className="avatar avatar-assistant">
          <SparklesIcon size={13} style={{ color: "var(--color-accent-insight)" }} />
        </div>
        <div className="assistant-content">
          <div className="bubble assistant">
            <p style={{ margin: 0 }}>{message.answer}</p>
          </div>

          <ResultCard result={message.result} />

          {message.chart_base64 && (
            <img
              src={`data:image/png;base64,${message.chart_base64}`}
              alt="Generated chart"
              className="generated-chart"
            />
          )}

          <button onClick={() => setShowCode((prev) => !prev)} className="code-toggle">
            {showCode ? <ChevronDownIcon size={13} /> : <ChevronRightIcon size={13} />}
            <CodeIcon size={13} />
            {showCode ? "Hide generated Pandas code" : "View generated Pandas code"}
          </button>
          {showCode && <pre className="code-block">{message.generated_code}</pre>}
        </div>
      </div>
    </div>
  );
}
