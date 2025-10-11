import { useMemo, useState } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { api } from "../lib/axios";
import { useQuery } from "@tanstack/react-query";
import ColumnVisibilityMenu from "../components/ColumnVisibilityMenu";

export default function UsersTable() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(() => Number(localStorage.getItem("pageSize")) || 20);
  const [sort, setSort] = useState<string[]>([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["users", page, pageSize, sort, globalFilter],
    queryFn: async () => {
      const params: any = { page, page_size: pageSize };
      if (sort.length) params.ordering = sort.join(",");
      if (globalFilter) params.search = globalFilter;
      const { data } = await api.get("/users/", { params });
      return data; // { results, count }
    }
  });

  const columns: ColumnDef<any>[] = [
    {
      accessorKey: "username",
      header: "Username",                       // string is fine
      cell: info => info.getValue(),            // cell renderer
    },
    {
      accessorKey: "email",
      header: ctx => <span>Email</span>,        // header renderer (HeaderContext)
      cell: ctx => <span>{ctx.getValue()}</span>, // cell renderer (CellContext)
    },
  ];

  const table = useReactTable({
    data,                // your row data
    columns,
    getCoreRowModel: getCoreRowModel(),
  });
  function onHeaderClick(colId: string, multi: boolean) {
    let next = [...sort];
    const i = next.findIndex(s => s.replace("-", "") === colId);
    if (i === -1) next.push(colId);
    else if (!next[i].startsWith("-")) next[i] = "-" + colId; else next.splice(i, 1);
    if (!multi) next = [next[next.length - 1]];
    setSort(next);
  }
  
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3 gap-2">
        <input className="input max-w-xs" placeholder="Search..." value={globalFilter} onChange={e=>{ setGlobalFilter(e.target.value); setPage(1); }} />
        <div className="flex items-center gap-3">
          <span className="text-sm">Rows per page</span>
          <select className="input" value={pageSize} onChange={e=>{ const v = Number(e.target.value); setPageSize(v); localStorage.setItem("pageSize", String(v)); setPage(1); }}>
            {[10,20,50,100].map(n=> <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="min-w-full">
          <thead className="bg-slate-100">
            {table.getHeaderGroups().map(hg => (
              <tr key={hg.id}>
                {hg.headers.map(h => (
                  <th key={h.id} className="text-left text-sm font-semibold px-3 py-2 cursor-pointer select-none"
                    onClick={(e)=> onHeaderClick(h.column.id, e.shiftKey)}>
                    {flexRender(h.column.columnDef.header, h.getContext())}
                    {(() => { const s = sort.find(x=>x.replace("-","")===h.column.id); if (!s) return null; return <span>{s.startsWith("-") ? " ↓" : " ↑"}</span>; })()}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {(isLoading ? Array.from({ length: 10 }).map((_,i)=>(
              <tr key={i} className={i%2?"bg-gray-50":"bg-white"}><td className="px-3 py-2" colSpan={columns.length}>Loading...</td></tr>
            )) : table.getRowModel().rows.map((row, i) => (
              <tr key={row.id} className={i%2?"bg-gray-50":"bg-white"}>
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-3 py-2 whitespace-nowrap">
                    {flexRender(cell.column.columnDef.cell ?? cell.column.columnDef.header, cell.getContext())}
                  </td>
                ))}
              </tr>
            )))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-3">
        <div className="flex gap-2">
          <button className="btn" onClick={()=> setPage(p=> Math.max(1, p-1))} disabled={page===1}>Prev</button>
          <span className="px-2">Page {page} / {data ? Math.ceil(data.count / pageSize) : "-"}</span>
          <button className="btn" onClick={()=> setPage(p=> p + 1)} disabled={data && page >= Math.ceil(data.count / pageSize)}>Next</button>
        </div>
        <ColumnVisibilityMenu table={table} />
      </div>
    </div>
  );
}
