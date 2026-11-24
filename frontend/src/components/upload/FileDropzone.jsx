import { useRef, useState } from "react";
import { FileSpreadsheetIcon, LoaderIcon, UploadCloudIcon } from "../../icons/Icons";

const ACCEPTED_EXTENSIONS = [".csv", ".xlsx", ".xls"];

function hasAcceptedExtension(file) {
  const name = file.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

/**
 * Drag-and-drop file picker built on native HTML5 drag events + a hidden
 * <input type="file"> — no react-dropzone. onDragOver must preventDefault or
 * the browser refuses the drop.
 */
export function FileDropzone({ onFileAccepted, isUploading, errorMessage }) {
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState(null);
  const inputRef = useRef(null);

  const validateAndAccept = (file) => {
    if (!file) return;
    if (!hasAcceptedExtension(file)) {
      setLocalError("Only .csv, .xlsx, and .xls files are supported.");
      return;
    }
    setLocalError(null);
    onFileAccepted(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    if (isUploading) return;
    validateAndAccept(event.dataTransfer.files?.[0]);
  };

  const handleInputChange = (event) => {
    validateAndAccept(event.target.files?.[0]);
    event.target.value = ""; // allow re-selecting the same file later
  };

  const combinedError = errorMessage ?? localError;

  return (
    <div className="upload-dropzone-wrapper">
      <div
        role="button"
        tabIndex={0}
        onClick={() => !isUploading && inputRef.current?.click()}
        onKeyDown={(event) => event.key === "Enter" && inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          if (!isUploading) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={[
          "upload-dropzone",
          isDragging ? "dragging" : "",
          isUploading ? "uploading" : "",
        ].join(" ").trim()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(",")}
          onChange={handleInputChange}
          disabled={isUploading}
          style={{ display: "none" }}
        />
        <div className="upload-dropzone-inner">
          {isUploading ? (
            <LoaderIcon size={32} className="spin" style={{ color: "var(--color-accent-data)" }} />
          ) : (
            <UploadCloudIcon size={32} style={{ color: "var(--color-text-muted)" }} />
          )}
          <div>
            <p className="upload-dropzone-title">
              {isUploading ? "Cleaning and indexing your data…" : "Drop a spreadsheet here, or click to browse"}
            </p>
            <p className="upload-dropzone-hint">Supports .csv, .xlsx, and .xls</p>
          </div>
        </div>
      </div>

      {combinedError && <p className="upload-error">{combinedError}</p>}

      <div className="upload-note">
        <FileSpreadsheetIcon size={14} style={{ flexShrink: 0, marginTop: "2px" }} />
        <p style={{ margin: 0 }}>
          Your file is cleaned with Pandas/NumPy, profiled automatically, and its schema is embedded for
          Atlas Vector Search — nothing leaves your own backend and MongoDB Atlas cluster.
        </p>
      </div>
    </div>
  );
}
