import { useState, useRef } from "react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";

const ACCEPT = [
  ".xlsx",
  ".xls",
  ".csv"
].join(",");

// Change this if your backend uses a different URL:
const IMPORT_ENDPOINT = "/import/excel/"; // e.g. "/profiles/import/" or "/admin/import/"

export default function ExcelImport() {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  function onPickFile(e: React.ChangeEvent<HTMLInputElement>) {
    setMessage(null);
    setError(null);
    setProgress(0);
    const f = e.target.files?.[0] || null;
    setFile(f);
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setMessage(null);
    setError(null);
    setProgress(0);
    const f = e.dataTransfer.files?.[0] || null;
    setFile(f);
  }

  function onDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);
    setError(null);

    if (!file) {
      setError("Please choose a file first.");
      return;
    }

    const form = new FormData();
    // Most DRF endpoints expect 'file' as the key. Change if your backend uses a different name.
    form.append("file", file, file.name);

    setSubmitting(true);
    try {
      await api.post(IMPORT_ENDPOINT, form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (evt) => {
          if (!evt.total) return;
          setProgress(Math.round((evt.loaded / evt.total) * 100));
        },
      });
      setMessage("Import completed successfully.");
      setFile(null);
      setProgress(0);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err: any) {
      const { message, fields } = extractApiError(err);
      let top = message || "Import failed.";
      if (fields) {
        // If backend returns row-level errors, collapse them for display
        const extra = Object.entries(fields)
          .map(([k, v]) => `${k}: ${(Array.isArray(v) ? v.join(" ") : String(v))}`)
          .join(" | ");
        if (extra) top += ` — ${extra}`;
      }
      setError(top);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-xl mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">Import from Excel/CSV</h1>

      <div
        className="border-2 border-dashed rounded-lg p-6 text-center mb-3 hover:bg-gray-50"
        onDrop={onDrop}
        onDragOver={onDragOver}
      >
        <p className="mb-2">Drag & drop a file here</p>
        <p className="text-xs text-gray-500 mb-4">Accepted: .xlsx, .xls, .csv</p>
        <button
          type="button"
          className="btn"
          onClick={() => inputRef.current?.click()}
        >
          Choose file
        </button>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          onChange={onPickFile}
          className="hidden"
        />
      </div>

      {file && (
        <div className="mb-3 text-sm">
          <span className="font-medium">Selected:</span> {file.name} ({Math.round(file.size / 1024)} KB)
        </div>
      )}

      {submitting && (
        <div className="w-full bg-gray-200 rounded h-2 mb-3 overflow-hidden">
          <div
            className="bg-blue-600 h-2 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {message && <p className="text-green-700 text-sm mb-2">{message}</p>}
      {error && <p className="text-red-600 text-sm mb-2">{error}</p>}

      <form onSubmit={onSubmit}>
        <div className="flex gap-2">
          <button className="btn" type="submit" disabled={!file || submitting}>
            {submitting ? "Uploading…" : "Start import"}
          </button>
          <a
            className="btn btn-ghost"
            href="/templates/import_template.xlsx"
            download
          >
            Download template
          </a>
        </div>
      </form>

      <p className="text-xs text-gray-500 mt-4">
        Tip: make sure your columns match the backend importer’s expectations (e.g. headers, date formats).
      </p>
    </div>
  );
}
