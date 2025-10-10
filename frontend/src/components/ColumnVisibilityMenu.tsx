import { Table } from "@tanstack/react-table";

type Props<T> = { table: Table<T> };
export default function ColumnVisibilityMenu<T>({ table }: Props<T>) {
  return (
    <div className="flex flex-wrap gap-2">
      {table.getAllLeafColumns().map((col) => (
        <label key={col.id} className="inline-flex items-center gap-1 text-sm">
          <input type="checkbox" checked={col.getIsVisible()} onChange={col.getToggleVisibilityHandler()} />
          {col.columnDef.header as any}
        </label>
      ))}
    </div>
  );
}
