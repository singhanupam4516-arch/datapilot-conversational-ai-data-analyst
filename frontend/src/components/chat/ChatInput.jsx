import { useState } from "react";
import { LoaderIcon, SendIcon } from "../../icons/Icons";

export function ChatInput({ onSend, isSending }) {
  const [value, setValue] = useState("");

  const submit = (event) => {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || isSending) return;
    onSend(trimmed);
    setValue("");
  };

  return (
    <form onSubmit={submit} className="chat-input-form">
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit(event);
          }
        }}
        placeholder="Ask a question about your data — e.g. Which region had the highest revenue drop?"
        rows={1}
      />
      <button type="submit" disabled={isSending || !value.trim()} className="btn btn-icon-only">
        {isSending ? <LoaderIcon size={16} className="spin" /> : <SendIcon size={16} />}
      </button>
    </form>
  );
}
