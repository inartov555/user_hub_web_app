import * as React from "react";

type Props = {
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

export default function ErrorAlert({ message, title }: Props) {
  const lines = splitLines(message);
  if (!lines.length) return null;

  return (
    <div
      role="alert"
      className="rounded-xl border border-red-200 bg-red-50 text-red-800
                 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-200 p-4"
    >
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
