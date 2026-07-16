"use client";

import { useRef, useState } from "react";
import { uploadJD } from "../lib/api";

interface JDUploadPopupProps {
  threadId: string;
  currentJdPath: string | null;
  onUploaded: (jdPath: string, filename: string) => void;
}

export default function JDUploadPopup({
  threadId,
  currentJdPath,
  onUploaded,
}: JDUploadPopupProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const hasJd = !!currentJdPath;
  const currentFilename = currentJdPath
    ? currentJdPath.split("/").pop() || currentJdPath.split("\\").pop() || "JD file"
    : null;

  const handleFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are accepted.");
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const result = await uploadJD(threadId, file);
      onUploaded(result.jd_path, result.filename);
      setShowModal(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    // Reset input so same file can be re-selected
    e.target.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <>
      {/* ─── Sticky Banner ─────────────────────────────── */}
      <div
        className={`
          sticky-jd-banner
          flex items-center justify-between gap-3 px-4 py-2.5
          border-b transition-all duration-300
          ${hasJd
            ? "bg-emerald-950/40 border-emerald-800/40"
            : "bg-amber-950/50 border-amber-800/40"
          }
        `}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          {/* Status icon */}
          <span className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center
            ${hasJd ? "bg-emerald-500/20" : "bg-amber-500/20"}`}>
            {hasJd ? (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                className="w-3.5 h-3.5 text-emerald-400">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                className="w-3.5 h-3.5 text-amber-400">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            )}
          </span>

          <div className="min-w-0">
            <p className={`text-xs font-medium truncate ${hasJd ? "text-emerald-300" : "text-amber-300"}`}>
              {hasJd
                ? `JD uploaded: ${currentFilename}`
                : "No Job Description uploaded — required before starting workflow"}
            </p>
          </div>
        </div>

        {/* Upload / Replace button */}
        <button
          id="jd-upload-btn"
          onClick={() => setShowModal(true)}
          className={`
            flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold
            transition-all duration-200 active:scale-95
            ${hasJd
              ? "bg-emerald-700/50 hover:bg-emerald-600/60 text-emerald-200 border border-emerald-700/60"
              : "bg-amber-600/70 hover:bg-amber-500/80 text-amber-100 border border-amber-600/60"
            }
          `}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            className="w-3.5 h-3.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          {hasJd ? "Replace JD" : "Upload JD"}
        </button>
      </div>

      {/* ─── Upload Modal ──────────────────────────────── */}
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={(e) => e.target === e.currentTarget && setShowModal(false)}
        >
          <div className="relative w-full max-w-md mx-4 bg-zinc-900 border border-zinc-700/60 rounded-2xl shadow-2xl overflow-hidden">
            {/* Modal header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
              <h2 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                  className="w-4 h-4 text-indigo-400">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                {hasJd ? "Replace Job Description" : "Upload Job Description"}
              </h2>
              <button
                id="jd-modal-close"
                onClick={() => setShowModal(false)}
                className="text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                  className="w-5 h-5">
                  <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>

            {/* Drop zone */}
            <div className="p-6">
              <div
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDrop}
                className={`
                  relative flex flex-col items-center justify-center gap-3
                  rounded-xl border-2 border-dashed cursor-pointer
                  py-10 px-6 text-center transition-all duration-200
                  ${isDragOver
                    ? "border-indigo-500 bg-indigo-500/10"
                    : "border-zinc-700 hover:border-zinc-500 bg-zinc-800/50 hover:bg-zinc-800"
                  }
                  ${isUploading ? "opacity-50 pointer-events-none" : ""}
                `}
              >
                {isUploading ? (
                  <>
                    <div className="w-10 h-10 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
                    <p className="text-sm text-zinc-400">Uploading...</p>
                  </>
                ) : (
                  <>
                    <div className="w-12 h-12 rounded-full bg-indigo-500/15 flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
                        className="w-6 h-6 text-indigo-400">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-zinc-200">
                        Drop your JD here, or{" "}
                        <span className="text-indigo-400 underline underline-offset-2">browse</span>
                      </p>
                      <p className="text-xs text-zinc-500 mt-1">PDF files only · Max 20 MB</p>
                    </div>
                  </>
                )}
              </div>

              <input
                ref={fileInputRef}
                id="jd-file-input"
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={handleFileChange}
              />

              {/* Error message */}
              {error && (
                <div className="mt-3 flex items-center gap-2 rounded-lg bg-red-950/50 border border-red-800/50 px-3 py-2">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                    className="w-4 h-4 text-red-400 flex-shrink-0">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                  </svg>
                  <p className="text-xs text-red-300">{error}</p>
                </div>
              )}

              {/* Current JD info */}
              {hasJd && (
                <div className="mt-3 flex items-center gap-2 rounded-lg bg-zinc-800/60 border border-zinc-700/50 px-3 py-2">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                    className="w-4 h-4 text-emerald-400 flex-shrink-0">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                  <p className="text-xs text-zinc-400 truncate">
                    Current: <span className="text-zinc-200">{currentFilename}</span>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
