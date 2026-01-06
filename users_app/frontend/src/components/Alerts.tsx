import * as React from "react";
import { AlertTriangle, CheckCircle, Info } from "lucide-react";

type ErrorAlertProps = {
  message?: unknown;
  title?: React.ReactNode;
};

function splitLines(raw: unknown): string[] {
  // Split by '\n', preserving spaces, tabs
  const normalized = String(raw ?? "")
    .replace(/\u00A0/g, " ")  // NBSP -> space
    .replace(/\\n/g, "\n");   // literal "\n" -> real newline
  return normalized
    .split(/\r?\n/)           // split by newline
    .map(s => s.replace(/\t/g, "    ").trimEnd()) // keep spaces; expand tabs if you want
    .filter(line => line.length > 0);
}

export default function ErrorAlert({ message, title }: ErrorAlertProps) {
  const lines = splitLines(message);
  if (!lines.length) return null;

  return (
    <div
      data-tag="errorAlert"
      role="alert"
      className="rounded-xl border border-red-200 bg-red-50 text-red-800
                 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-200 p-4"
    >
      <AlertTriangle className="h-6 w-6 mb-2 mt-2" />
      {title ? <div className="font-semibold mb-2">{title}</div> : null}
      <ul className="space-y-1">
        {lines.map((line, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="select-none mt-[2px]"></span>
            <span>{line}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function SimpleErrorMessage({ errorUi, errorBackend }: { errorUi?: string, errorBackend?: string | null; } ) {
  /*
   * errorUi (string): this one describes UI error, e.g., auth.loginFailed
   * errorBackend (string): backend error
   */
  if (!errorUi && !errorBackend) return null;
  // const text = [errorUi, errorBackend].filter(Boolean).join(" ");
  return (
    <div data-tag="simpleErrorMessage"
         className="
           rounded-xl border border-rose-200/60 bg-rose-50/40 px-3 py-2
           backdrop-blur-sm text-sm text-rose-600 whitespace-pre-line
           dark:border-rose-500/25 dark:bg-rose-950/20 dark:text-rose-300
         "
    >
      <div className="mt-4 mb-2 text-sm flex">
        <AlertTriangle className="h-6 w-6 text-rose-600 dark:text-rose-300" />
        {errorUi && <span className="ml-4 mt-1">{errorUi}</span>}
      </div>
      {/* <p className="whitespace-pre-line ml-2">{text}</p> */}
      {errorBackend && <span>{errorBackend}</span>}
    </div>
  );
}

export function SimpleSuccessMessage({ message, block }: { message?: string; block?: React.ReactElement; }) {
  /*
   * It maybe either message or block, or both
   */
  if (!message && !block) return null;

  return (
    <div
      data-tag="simpleSuccessMessage"
      className="
        rounded-xl border border-emerald-200/60 bg-emerald-50/40 px-3 py-2
        backdrop-blur-sm text-sm text-emerald-800 whitespace-pre-line
        dark:border-emerald-400/25 dark:bg-emerald-950/20 dark:text-emerald-100
      "
    >
      <CheckCircle className="h-6 w-6 mb-2 mt-2 text-emerald-800 dark:text-emerald-100" />
      { message && <span>{message}</span> }
      <div className="ml-2">{ block }</div>
    </div>
  );
}

export function SimpleInfoMessage({ message, block }: { message?: string; block?: React.ReactElement; }) {
  /*
   * It maybe either message or block, or both
   */
  if (!message && !block) return null;

  return (
    <div
      data-tag="simpleInfoMessage"
      className="
        rounded-xl border border-sky-200/60 bg-sky-50/40 px-3 py-2
        backdrop-blur-sm text-sm text-sky-800 whitespace-pre-line
        dark:border-sky-400/25 dark:bg-sky-950/20 dark:text-sky-200
      "
    >
      <Info className="h-6 w-6 mb-2 mt-2 text-sky-800 dark:text-sky-200" />
      { message && <span>{message}</span> }
      <div className="ml-2">{ block }</div>
    </div>
  );
}
