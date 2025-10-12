import * as React from "react";
import { useMemo, useState } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  VisibilityState,
  useReactTable,
} from "@tanstack/react-table";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/axios";

import { Button } from "../components/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/card";
import { Input } from "../components/input";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/dropdown-menu";
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Columns, ArrowUpDown } from "lucide-react";

type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

export default function UsersTable() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(() => Number(localStorage.getItem("pageSize")) || 20);
  const [sort, setSort] = useState<string[]>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});

  const { data, isLoading } = useQuery({
    queryKey: ["users", page, pageSize, sort, globalFilter],
    queryFn: async () => {
      const params: Record<string, unknown> = { page, page_size: pageSize };
      if (sort.length) params.ordering = sort.join(",");
      if (globalFilter) params.search = globalFilter;
      const { data } = await api.get("/users/", { params });
      return data as { results: User[]; count: number };
    },
  });

  const rows = useMemo(() => data?.results ?? [], [data]);

  const columns = useMemo<ColumnDef<User>[]>(() => [
    {
      accessorKey: "username",
      header: ({ column }) => (
        <button
          type="button"
          className="inline-flex items-center gap-1"
          onClick={(e) => column.toggleSorting(column.getIsSorted() === "asc", e.shiftKey)}
          title="Click to sort. Shift+Click for multi-sort"
        >
          Username <ArrowUpDown className="h-4 w-4" />
        </button>
      ),
      cell: (info) => <span className="font-medium break-words">{info.getValue() as string}</span>,
      size: 220,
      enableResizing: true,
    },
    {
      accessorKey: "email",
      header: ({ column }) => (
        <button
          type="button"
          className="inline-flex items-center gap-1"
          onClick={(e) => column.toggleSorting(column.getIsSorted() === "asc", e.shiftKey)}
          title="Click to sort. Shift+Click for multi-sort"
        >
          Email <ArrowUpDown className="h-4 w-4" />
        </button>
      ),
      cell: (ctx) => <span className="break-words">{ctx.getValue<string>()}</span>,
      size: 280,
      enableResizing: true,
    },
    {
      accessorKey: "first_name",
      header: ({ column }) => (
        <button
          type="button"
          className="inline-flex items-center gap-1"
          onClick={(e) => column.toggleSorting(column.getIsSorted() === "asc", e.shiftKey)}
          title="Click to sort. Shift+Click for multi-sort"
        >
          First name <ArrowUpDown className="h-4 w-4" />
        </button>
      ),
      cell: (ctx) => <span className="break-words">{ctx.getValue<string>()}</span>,
      size: 180,
      enableResizing: true,
    },
    {
      accessorKey: "last_name",
      header: ({ column }) => (
        <button
          type="button"
          className="inline-flex items-center gap-1"
          onClick={(e) => column.toggleSorting(column.getIsSorted() === "asc", e.shiftKey)}
          title="Click to sort. Shift+Click for multi-sort"
        >
          Last name <ArrowUpDown className="h-4 w-4" />
        </button>
      ),
      cell: (ctx) => <span className="break-words">{ctx.getValue<string>()}</span>,
      size: 180,
      enableResizing: true,
    },
  ], []);

  const table = useReactTable({
    data: rows,
    columns,
    state: {
      sorting,
      columnVisibility,
      pagination: { pageIndex: page - 1, pageSize },
    },
    onSortingChange: setSorting,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    // column resizing
    columnResizeMode: "onChange",
    enableColumnResizing: true,
  });

  // keep localStorage in sync for pageSize
  React.useEffect(() => {
    localStorage.setItem("pageSize", String(pageSize));
  }, [pageSize]);

  if (isLoading) return <div>Loading…</div>;

  return (
    <Card className="w-full mx-auto">
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <CardTitle className="text-xl">People</CardTitle>
        <div className="flex items-center gap-2">
          <Input
            placeholder="Search…"
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="w-48"
          />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2">
                <Columns className="h-4 w-4" /> Columns
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>Toggle columns</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {table.getAllLeafColumns().map((col) => {
                // Render a readable label for the menu
                const label =
                  typeof col.columnDef.header === "string"
                    ? col.columnDef.header
                    : col.id;
                return (
                  <DropdownMenuCheckboxItem
                    key={col.id}
                    checked={col.getIsVisible()}
                    onCheckedChange={(v) => col.toggleVisibility(Boolean(v))}
                  >
                    {label}
                  </DropdownMenuCheckboxItem>
                );
              })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>

      <CardContent>
        <div className="overflow-auto rounded-xl border">
          <table className="w-full text-sm table-auto border-collapse">
            <thead className="bg-muted/50">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id} className="border-b">
                  {headerGroup.headers.map((header) => {
                    const isSorted = header.column.getIsSorted();
                    const sortIndex = header.column.getSortIndex();
                    return (
                      <th
                        key={header.id}
                        colSpan={header.colSpan}
                        style={{ width: header.getSize() }}
                        className="relative select-none px-3 py-2 text-left font-semibold align-middle group whitespace-normal break-words"
                      >
                        {header.isPlaceholder ? null : (
                          <div
                            className="inline-flex items-center gap-1 cursor-pointer"
                            onClick={(e) => header.column.toggleSorting(isSorted === "asc", e.shiftKey)}
                            title="Click to sort. Shift+Click for multi-sort"
                          >
                            {flexRender(header.column.columnDef.header, header.getContext())}
                            {typeof sortIndex === "number" && (
                              <span className="text-xs text-muted-foreground">#{sortIndex + 1}</span>
                            )}
                          </div>
                        )}
                        {/* Resizer handle */}
                        {header.column.getCanResize() && (
                          <div
                            onMouseDown={header.getResizeHandler()}
                            onTouchStart={header.getResizeHandler()}
                            className="absolute right-0 top-0 h-full w-1 cursor-col-resize select-none touch-none bg-transparent group-hover:bg-border"
                          />
                        )}
                      </th>
                    );
                  })}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td className="px-3 py-6 text-center text-muted-foreground" colSpan={columns.length}>
                    No results
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr key={row.id} className="border-b hover:bg-muted/40">
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        style={{ width: cell.column.getSize() }}
                        className="px-3 py-2 align-middle whitespace-normal break-words"
                      >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination controls */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => (table.setPageIndex(0), setPage(1))}
              disabled={!table.getCanPreviousPage()}
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => (table.previousPage(), setPage((p) => Math.max(1, p - 1)))}
              disabled={!table.getCanPreviousPage()}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => (table.nextPage(), setPage((p) => p + 1))}
              disabled={!table.getCanNextPage()}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const last = Math.max(0, table.getPageCount() - 1);
                table.setPageIndex(last);
                setPage(last + 1);
              }}
              disabled={!table.getCanNextPage()}
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <span>
              Page <strong>{table.getState().pagination.pageIndex + 1}</strong> of {table.getPageCount() || 1}
            </span>
            <label className="flex items-center gap-2">
              Rows per page
              <select
                className="rounded-md border bg-background px-2 py-1"
                value={table.getState().pagination.pageSize}
                onChange={(e) => {
                  const ps = Number(e.target.value);
                  table.setPageSize(ps);
                  setPageSize(ps);
                }}
              >
                {[10, 20, 30, 50, 100].map((ps) => (
                  <option key={ps} value={ps}>
                    {ps}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
