import { useEffect, useRef, useState } from "react";
import { MessageSquareIcon, SparklesIcon } from "../icons/Icons";
import { ChatInput } from "../components/chat/ChatInput";
import { MessageBubble } from "../components/chat/MessageBubble";
import { api, ApiError } from "../api/client";

const EXAMPLE_QUESTIONS = [
  "What are the top 5 rows by value in the largest numeric column?",
  "Which category appears most often?",
  "Show me the average of each numeric column, grouped by the main category column.",
];

export function ChatPage({ session }) {
  const [messages, setMessages] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoadingHistory(true);
    api
      .getChatHistory(session.session_id)
      .then((history) => {
        if (!cancelled) setMessages(history.messages);
      })
      .catch(() => {
        /* A brand-new session with no history yet is expected, not an error. */
      })
      .finally(() => {
        if (!cancelled) setIsLoadingHistory(false);
      });
    return () => {
      cancelled = true;
    };
  }, [session.session_id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const handleSend = async (text) => {
    setErrorMessage(null);
    setIsSending(true);
    try {
      const response = await api.sendChatMessage(session.session_id, text);
      setMessages((prev) => [...prev, response]);
    } catch (error) {
      setErrorMessage(error instanceof ApiError ? error.message : "The AI pipeline failed. Try rephrasing.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h1>
          <MessageSquareIcon size={18} style={{ color: "var(--color-accent-insight)" }} />
          Chat with {session.filename}
        </h1>
      </div>

      <div className="chat-messages">
        {isLoadingHistory ? (
          <p className="chat-status">Loading conversation…</p>
        ) : messages.length === 0 ? (
          <div className="chat-empty-state">
            <SparklesIcon size={26} style={{ color: "var(--color-accent-insight)" }} />
            <div>
              <p>Ask anything about your data</p>
              <p className="chat-empty-hint">
                Your question is embedded, matched against this dataset's schema, and answered by an LLM
                writing real Pandas code.
              </p>
            </div>
            <div className="example-question-list">
              {EXAMPLE_QUESTIONS.map((question) => (
                <button key={question} onClick={() => handleSend(question)} className="example-question">
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message, index) => <MessageBubble key={index} message={message} />)
        )}

        {isSending && <p className="chat-status">DataPilot is writing and running Pandas code…</p>}
        {errorMessage && <p className="chat-error">{errorMessage}</p>}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-bar">
        <ChatInput onSend={handleSend} isSending={isSending} />
      </div>
    </div>
  );
}
