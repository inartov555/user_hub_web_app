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
    <thead>
      {table.getHeaderGroups().map(hg => (
        <tr key={hg.id}>
          {hg.headers.map(h => (
            <th key={h.id}>
              {h.isPlaceholder
                ? null
                : flexRender(h.column.columnDef.header, h.getContext())}
              {/* ^^^^^^^^^ header renderer + HeaderContext */}
            </th>
          ))}
        </tr>
      ))}
    </thead>
    <tbody>
      {table.getRowModel().rows.map(row => (
        <tr key={row.id}>
          {row.getVisibleCells().map(cell => (
            <td key={cell.id}>
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
              {/* ^^^^^ cell renderer + CellContext */}
            </td>
          ))}
        </tr>
      ))}
    </tbody>);
}
