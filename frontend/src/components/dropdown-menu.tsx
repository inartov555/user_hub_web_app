import * as React from "react";

export function DropdownMenu({ children }: { children: React.ReactNode }) {
  return <div className="relative inline-block">{children}</div>;
}
export function DropdownMenuTrigger({ asChild, children }: { asChild?: boolean; children: React.ReactNode }) {
  return <>{children}</>;
}
export function DropdownMenuContent(
  { align = "start", className = "", children }:
  { align?: "start" | "end"; className?: string; children: React.ReactNode }
) {
  return (
    <div className={`absolute z-10 mt-2 min-w-[12rem] rounded-md border bg-white p-2 shadow-lg
                    ${align === "end" ? "right-0" : "left-0"} ${className}`}>
      {children}
    </div>
  );
}
export function DropdownMenuLabel({ children }: { children: React.ReactNode }) {
  return <div className="px-2 py-1 text-xs font-medium text-slate-500">{children}</div>;
}
export function DropdownMenuSeparator() {
  return <div className="my-2 h-px bg-slate-200" />;
}
export function DropdownMenuCheckboxItem(
  { checked, onCheckedChange, children, ...props }:
  { checked?: boolean; onCheckedChange?: (v: boolean) => void; children: React.ReactNode } & React.HTMLAttributes<HTMLDivElement>
) {
  return (
    <div
      role="menuitemcheckbox"
      aria-checked={checked}
      onClick={() => onCheckedChange?.(!checked)}
      className="flex cursor-pointer items-center gap-2 rounded px-2 py-1.5 hover:bg-slate-50"
      {...props}
    >
      <input type="checkbox" readOnly checked={!!checked} />
      <span>{children}</span>
    </div>
  );
}
