import React, { useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import { FileSpreadsheet } from "lucide-react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";
import { Input } from "../components/input";
import Button from "../components/button";
import UnifiedTitle from "../components/UnifiedTitle";
import { SimpleErrorMessage } from "../components/ErrorAlert";

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
      // Clearing the error message in case of successful import
      setError("");
    } catch (err: any) {
      const parsed = extractApiError(err as unknown);
      setError(`${t("excelImport.excelImportFailure")} ${parsed.message}`);
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
      const parsed = extractApiError(err as unknown);
      setError(`${t("excelImport.templateDownloadFailed")} ${parsed.message}`);
    }
  }

  return (
    <div className="
           max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800
           dark:text-slate-100 dark:border-slate-700
         "
    >
      <UnifiedTitle icon={<FileSpreadsheet className="h-4 w-4" />} title={t("excelImport.title")} />
      <p className="mb-4 max-w-prose text-sm sm:text-[0.95rem] leading-relaxed text-slate-600 dark:text-slate-300">
        <span>{t("excelImport.fileUploadMessage")} </span>
        <br/>
        <span>{t("signup.email")} | </span>
        <span>{t("signup.username")} | </span>
        <span>{t("users.firstName")} | </span>
        <span>{t("users.lastName")} | </span>
        <span>{t("excelImport.bio")}</span>.
      </p>

      <form onSubmit={onSubmit} className="space-y-3">
        <Input
          key={inputKey}
          ref={inputRef}
          type="file"
          id="excelImportFile"
          accept=".xlsx,.xls,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv"
          onChange={onFileChange}
          onClick={(e) => { (e.currentTarget as HTMLInputElement).value = ""; }} // allow re-select same file
        />
        {file && (
          <div className="text-sm text-gray-600 dark:text-slate-300 mt-1">{t("excelImport.selectedFile")} {file.name}</div>
        )}

        {error && <SimpleErrorMessage errorBackend={error} />}
        <div className="flex gap-2">
          <Button id="importTemplate" type="submit">
            {submitting ? t("excelImport.uploading") : t("excelImport.startImport")}
          </Button>

          {/* If you rely on cookie auth, a plain anchor works: href={`${api.defaults.baseURL}/import-excel/`} */}
          {accessToken ? (
            <Button id="downloadTemplate" onClick={downloadTemplate}>
              {t("excelImport.downloadTemplate")}
            </Button>
          ) : (
            <a className="btn btn-ghost px-4 py-2 rounded-xl border" href={`${api.defaults.baseURL}/import-excel/`} download>
              {t("excelImport.downloadTemplate")}
            </a>
          )}
        </div>
      </form>

      {message && (
        <div className="mt-4 text-sm p-2 rounded-xl border bg-gray-50 dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">{message}</div>
      )}

      {summary && (
        <div className="mt-4 p-3 rounded-2xl border bg-white
                dark:bg-slate-800 dark:border-slate-700">
          <div data-tag="resultSuccessTitle" className="font-medium mb-2">{t("excelImport.result")}</div>
          <ul data-tag="resultSuccessBody" className="text-sm space-y-1">
            <li>{t("excelImport.processed")} <span className="font-semibold">{summary.processed}</span></li>
            <li>{t("excelImport.created")} <span className="font-semibold">{summary.created}</span></li>
            <li>{t("excelImport.updated")} <span className="font-semibold">{summary.updated}</span></li>
          </ul>

          {summary.errors?.length ? (
            <div className="mt-3">
              <div className="font-medium mb-1">Errors ({summary.errors.length})</div>
              <div className="max-h-48 overflow-auto border rounded-xl">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-white dark:bg-slate-900">
                    <tr>
                      <th className="text-left p-2 border-b w-24">Row</th>
                      <th className="text-left p-2 border-b">Message</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.errors.map((e, idx) => (
                      <tr key={idx} className="odd:bg-gray-50 dark:odd:bg-slate-800">
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
