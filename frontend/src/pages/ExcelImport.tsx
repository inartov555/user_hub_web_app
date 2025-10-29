import React, { useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";
import { Input } from "../components/input";

// Tailwind + shadcn/ui-style minimal UI without extra deps
// Drop this component anywhere in your frontend. It provides:
// - File picker + submit to POST /api/import-excel/
// - "Download template" that calls GET /api/import-excel/ (same endpoint) and downloads the .xlsx
// - Uses Bearer token (Authorization header) from localStorage
// - Shows success summary (created/updated/errors)

export default function ExcelImportPanel() {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [summary, setSummary] = useState<null | {
    created: number;
    updated: number;
    processed: number;
    errors: { row: number; msg: string }[];
  }>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [inputKey, setInputKey] = useState(0);
  const { accessToken } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(null);
    setSummary(null);
    const input = e.currentTarget;
    const a_file = input.files?.[0] || null;
    console.log('picked:', a_file?.name);
    setFile(a_file);
  };

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || submitting) return;
    setSubmitting(true);
    setMessage(null);
    setSummary(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const resp = await api.post(`/import-excel/`, form, {
        headers: accessToken ? { Authorization: `Bearer ${accessToken}`, "Content-Type": `multipart/form-data` } : undefined,
        // onUploadProgress: (e) => { /* optional progress */ },
      });

      const payload = resp?.data;
      setSummary(payload?.result ?? payload);
      setMessage(t("excelImport.importSuccessful"));

      // Reset the input for the *next* upload (without interfering with current display)
      setFile(null);
      setInputKey((k) => k + 1);
    } catch (err: any) {
      setMessage(err.message || "Import failed");
      const parsed = extractApiError(err as unknown);
      setError(`Excel upload failure: ${parsed.message}`);
    } finally {
      setSubmitting(false);
    }
  }

  async function downloadTemplate(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    try {
      const resp = await api.get(`/import-excel/`, {
        headers: accessToken ? { Authorization: `Bearer ${accessToken}`, "Content-Type": `multipart/form-data` } : undefined,
        responseType: "blob",
      });
      const fileBlob = new Blob([resp.data]);
      const url = window.URL.createObjectURL(fileBlob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "import_template.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setMessage((err as Error).message || "Failed to download template");
      const parsed = extractApiError(err as unknown);
      setError(`Excel template download failure: ${parsed.message}`);
    }
  }

  return (
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border">
      <h2 className="text-xl font-semibold mb-3">Excel import</h2>
      <p className="text-sm text-gray-600 mb-4">{t("excelImport.fileUploadMessage")} <code>{t("signup.email")}</code>, <code>{t("auth.username")}</code>, <code>{t("users.firstName")}</code>, <code>{t("users.lastName")}</code>, <code>{t("excelImport.bio")}</code>.</p>

      <form onSubmit={onSubmit} className="space-y-3">
        <Input
          key={inputKey}
          ref={inputRef}
          type="file"
          name="file"
          accept=".xlsx,.xls,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv"
          onChange={onFileChange}
          onClick={(e) => { (e.currentTarget as HTMLInputElement).value = ""; }} // allow re-select same file
          className="
            block w-full text-sm text-gray-900 !appearance-auto
            file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border
            file:bg-gray-50 file:hover:bg-gray-100 file:cursor-pointer
          "
        />
        {file && (
          <div className="text-sm text-gray-600 mt-1">{t("excelImport.uploading")} {file.name}</div>
        )}

        <div className="flex gap-2">
          <button className="btn px-4 py-2 rounded-xl bg-black text-white disabled:opacity-50" type="submit" disabled={!file || submitting}>
            {submitting ? t("excelImport.uploading") : t("excelImport.startImport")}
          </button>

          {/* If you rely on cookie auth, a plain anchor works: href={`${api.defaults.baseURL}/import-excel/`} */}
          {accessToken ? (
            <button className="btn btn-ghost px-4 py-2 rounded-xl border" onClick={downloadTemplate}>
              {t("excelImport.downloadTemplate")}
            </button>
          ) : (
            <a className="btn btn-ghost px-4 py-2 rounded-xl border" href={`${api.defaults.baseURL}/import-excel/`} download>
              {t("excelImport.downloadTemplate")}
            </a>
          )}
        </div>
      </form>

      {message && (
        <div className="mt-4 text-sm p-2 rounded-xl border bg-gray-50">{message}</div>
      )}

      {summary && (
        <div className="mt-4 p-3 rounded-2xl border">
          <div className="font-medium mb-2">{t("excelImport.result")}</div>
          <ul className="text-sm space-y-1">
            <li>{t("excelImport.processed")} <span className="font-semibold">{summary.processed}</span></li>
            <li>{t("excelImport.created")} <span className="font-semibold">{summary.created}</span></li>
            <li>{t("excelImport.updated")} <span className="font-semibold">{summary.updated}</span></li>
          </ul>

          {summary.errors?.length ? (
            <div className="mt-3">
              <div className="font-medium mb-1">Errors ({summary.errors.length})</div>
              <div className="max-h-48 overflow-auto border rounded-xl">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-white">
                    <tr>
                      <th className="text-left p-2 border-b w-24">Row</th>
                      <th className="text-left p-2 border-b">Message</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.errors.map((e, idx) => (
                      <tr key={idx} className="odd:bg-gray-50">
                        <td className="p-2 border-b">{e.row}</td>
                        <td className="p-2 border-b">{e.msg}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
