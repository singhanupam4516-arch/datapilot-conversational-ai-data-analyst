/**
 * API client using the browser's native fetch (no axios). JSDoc typedefs
 * mirror backend/app/models/schemas.py for editor autocomplete.
 *
 * @typedef {Object} UploadResponse
 * @property {string} session_id
 * @property {string} filename
 * @property {number} row_count
 * @property {number} column_count
 * @property {{name: string, dtype: string}[]} columns
 * @property {string} uploaded_at
 *
 * @typedef {Object} EDAResponse
 * @property {Object} numeric_summary
 * @property {Object} categorical_summary
 * @property {{column: string, chart_type: string, image_base64: string}[]} distribution_charts
 * @property {string|null} correlation_heatmap
 *
 * @typedef {Object} ChatMessage
 * @property {string} question
 * @property {string} answer
 * @property {string} generated_code
 * @property {*} result
 * @property {string|null} chart_base64
 * @property {string} timestamp
 */

// Vite exposes build-time env vars via import.meta.env, prefixed VITE_.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export class ApiError extends Error {}

/** Every backend error body is {"detail": "..."} (FastAPI's HTTPException shape). */
async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, options);
  } catch {
    throw new ApiError("Could not reach the backend. Is it running?");
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // Response wasn't JSON — fall back to the status text set above.
    }
    throw new ApiError(detail);
  }

  return response.json();
}

export const api = {
  /** Phase 1 — upload a CSV/XLSX, get back a session_id + column metadata. */
  uploadSpreadsheet(file) {
    const formData = new FormData();
    formData.append("file", file);
    return request("/upload", { method: "POST", body: formData });
  },

  /** Phase 2 — fetch computed stats + chart images for the dashboard. */
  getEda(sessionId) {
    return request(`/eda/${sessionId}`);
  },

  /** Phase 4 — ask a question, get back the LLM's code, result, and answer. */
  sendChatMessage(sessionId, message) {
    return request(`/chat/${sessionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
  },

  /** Chat history so a refreshed/reopened session doesn't lose context. */
  getChatHistory(sessionId) {
    return request(`/sessions/${sessionId}/history`);
  },
};
