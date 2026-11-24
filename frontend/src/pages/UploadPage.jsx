import { useState } from "react";
import { FileDropzone } from "../components/upload/FileDropzone";
import { api, ApiError } from "../api/client";

export function UploadPage({ onUploadComplete }) {
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleFileAccepted = async (file) => {
    setIsUploading(true);
    setErrorMessage(null);
    try {
      const session = await api.uploadSpreadsheet(file);
      onUploadComplete(session);
    } catch (error) {
      setErrorMessage(error instanceof ApiError ? error.message : "Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <h1 className="upload-title">Turn a spreadsheet into a conversation</h1>
      <p className="upload-subtitle">
        Upload a CSV or Excel file. DataPilot cleans it, profiles it, and lets you ask questions about it
        in plain English — answered by an open-source LLM writing live Pandas code.
      </p>
      <FileDropzone onFileAccepted={handleFileAccepted} isUploading={isUploading} errorMessage={errorMessage} />
    </div>
  );
}
