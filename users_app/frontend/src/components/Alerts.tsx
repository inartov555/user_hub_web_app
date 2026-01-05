import * as React from "react";
import { AlertTriangle, CheckCircle, Info } from "lucide-react";

type ErrorAlertProps = {
  message?: unknown;
  title?: React.ReactNode;
};

type SimpleErrorMessageProps = {
  errorUi?: string;
  errorBackend?: string | null;
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
      <AlertTriangle className="h-4 w-4 mb-2" />
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

export function SimpleErrorMessage({ errorUi, errorBackend }: SimpleErrorMessageProps) {
  /*
   * errorUi (string): this one describes UI error, e.g., auth.loginFailed
   * errorBackend (string): backend error
   */
  if (!errorBackend) return null;
  const text = [errorUi, errorBackend].filter(Boolean).join(" ");
  return (
    <div data-tag="simpleErrorMessage"
         className="
           rounded-xl border border-rose-200/60 bg-rose-50/40 px-3 py-2
           backdrop-blur-sm text-sm text-rose-700 whitespace-pre-line
           dark:border-rose-500/25 dark:bg-rose-950/20 dark:text-rose-200
         "
    >
      <AlertTriangle className="h-4 w-4 mb-2" />
      <p className="text-red-600 text-sm whitespace-pre-line">{text}</p>
    </div>
  );
}
