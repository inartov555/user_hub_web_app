import * as React from "react";
import { useMemo, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  SortingState,
  VisibilityState,
  useReactTable,
} from "@tanstack/react-table";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import type { RowSelectionState } from "@tanstack/react-table";
import { api } from "../lib/axios";

import { Button } from "../components/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/card";
import { Input } from "../components/input";
import { Checkbox } from "../components/checkbox";
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Columns, ArrowUpDown } from "lucide-react";

type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

// NEW: helper to turn TanStack sorting -> DRF `ordering` (e.g. ["username", "-email"])
const toOrdering = (s: SortingState) => s.map(({ id, desc }) => (desc ? `-${id}` : id));

type Props = {
  data: User[];
  onResetPasswords?: (userIds: number[]) => Promise<void> | void;
};

export default function UsersTable() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(() => Number(localStorage.getItem("pageSize")) || 20);
  const [sort, setSort] = useState<string[]>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [showColumns, setShowColumns] = useState(false); // NEW: controls menu visibility
  const [rowSelection, setRowSelection] = React.useState<RowSelectionState>({});
  const queryClient = useQueryClient();
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [pwUser, setPwUser] = useState<User | null>(null);
  const [pw1, setPw1] = useState("");
  const [pw2, setPw2] = useState("");
  const [pwLoading, setPwLoading] = useState(false);
  const [pwError, setPwError] = useState<string | null>(null);
  const closePw = () => { setPwUser(null); setPw1(""); setPw2(""); setPwError(null); };

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

  const handleDeleteSelected = async () => {
    const ids = table.getSelectedRowModel().flatRows.map((r) => r.original.id);
    if (!ids.length) return;

    /*
    // Window alert confirmation for user deletion
    if (!window.confirm(`Delete ${ids.length} selected user(s)? This cannot be undone.`)) {
      return;
    }
    */

    setDeleting(true);
    setDeleteError(null);
    try {
      // Try bulk endpoint first (adjust path if yours differs)
      const bulk = await api.post("/users/bulk-delete/", { ids }, { validateStatus: () => true });

      if (!(bulk.status >= 200 && bulk.status < 300)) {
        // Fallback: delete one-by-one
        const results = await Promise.allSettled(
          ids.map((id) => api.delete(`/users/${id}/`, { validateStatus: () => true }))
        );
        const failed = results.filter(
          (r) => r.status === "rejected" || (r.status === "fulfilled" && r.value.status >= 400)
        );
        if (failed.length) {
          setDeleteError(`Failed to delete ${failed.length} of ${ids.length} users.`);
        }
      }

      // clear selection + refresh list
      setRowSelection({});
      await queryClient.invalidateQueries({ queryKey: ["users"] });
    } catch (e: any) {
      setDeleteError(e?.message || "Failed to delete selected users.");
    } finally {
      setDeleting(false);
    }
  };

  const columns = useMemo<ColumnDef<User>[]>(() => [
    {
      id: "select",
      header: ({ table }) => {
        const all = table.getIsAllRowsSelected();
        const some = table.getIsSomeRowsSelected();
        return (
          <div className="px-2">
            <Checkbox
              checked={all}
              indeterminate={!all && some}
              onChange={(e) => table.toggleAllRowsSelected(e.currentTarget.checked)}
              aria-label="Select all"
            />
          </div>
        );
      },
      cell: ({ row }) => (
        <div className="px-2">
          <Checkbox
            checked={row.getIsSelected()}
            indeterminate={row.getIsSomeSelected()}
            onChange={(e) => row.toggleSelected(e.currentTarget.checked)}
            aria-label="Select row"
          />
        </div>
      ),
      size: 48,
      enableResizing: false,
      enableSorting: false,
    },
    {
      accessorKey: "username",
      header: ({ column }) => (
        <button
          type="button"
          className="inline-flex items-center gap-1"
          // NEW: allow Shift OR Ctrl/⌘ for multi-sort
          onClick={(e) =>
            column.toggleSorting(column.getIsSorted() === "asc", e.shiftKey || e.ctrlKey || e.metaKey)
          }
          title="Click to sort; hold Shift/Ctrl/⌘ to multi-sort"
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
          onClick={(e) =>
            column.toggleSorting(column.getIsSorted() === "asc", e.shiftKey || e.ctrlKey || e.metaKey)
          }
          title="Click to sort; hold Shift/Ctrl/⌘ to multi-sort"
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
          onClick={(e) =>
            column.toggleSorting(column.getIsSorted() === "asc", e.shiftKey || e.ctrlKey || e.metaKey)
          }
          title="Click to sort; hold Shift/Ctrl/⌘ to multi-sort"
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
          onClick={(e) =>
            column.toggleSorting(column.getIsSorted() === "asc", e.shiftKey || e.ctrlKey || e.metaKey)
          }
          title="Click to sort; hold Shift/Ctrl/⌘ to multi-sort"
        >
          Last name <ArrowUpDown className="h-4 w-4" />
        </button>
      ),
      cell: (ctx) => <span className="break-words">{ctx.getValue<string>()}</span>,
      size: 180,
      enableResizing: true,
    },
    {
      id: "change_password_action",
      header: "Change Password",
      enableSorting: false,
      size: 180,
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/users/${row.original.id}/change-password`)}
            title="Change password"
          >
            Change password
          </Button>
        </div>
      ),
    },
  ], [navigate]);

  // NEW: keep server 'ordering' in sync with TanStack multi-sort
  const handleSortingChange = (updater: React.SetStateAction<SortingState>) => {
    const next = typeof updater === "function" ? (updater as (prev: SortingState) => SortingState)(sorting) : updater;
    setSorting(next);
    setSort(toOrdering(next));
    setPage(1);
  };

  const table = useReactTable({
    data: rows,
    columns,
    state: {
      sorting,
      columnVisibility,
      pagination: { pageIndex: page - 1, pageSize },
      rowSelection,
    },
    onRowSelectionChange: setRowSelection,
    enableRowSelection: true,
    onSortingChange: handleSortingChange, // NEW
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    // IMPORTANT: server-side sorting – don't sort on client
    manualSorting: true, // NEW
    // keep pagination + resizing
    getPaginationRowModel: getPaginationRowModel(),
    columnResizeMode: "onChange",
    enableColumnResizing: true,
  });

  // keep localStorage in sync for pageSize
  useEffect(() => {
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

          {/* Columns menu (headless) */}
          <div className="relative">
            <Button variant="outline" size="sm" className="gap-2" onClick={() => setShowColumns((v) => !v)}>
              <Columns className="h-4 w-4" /> Columns
            </Button>
            {showColumns && (
              <div
                className="absolute right-0 z-10 mt-2 w-56 rounded-md border bg-white p-2 shadow-lg"
                role="menu"
              >
                <div className="px-2 py-1 text-xs font-medium text-slate-500">Toggle columns</div>
                <div className="my-2 h-px bg-slate-200" />
                {table.getAllLeafColumns().map((col) => {
                  const label = typeof col.columnDef.header === "string" ? col.columnDef.header : col.id;
                  return (
                    <label key={col.id} className="flex cursor-pointer items-center gap-2 rounded px-2 py-1.5 hover:bg-slate-50">
                      <input
                        type="checkbox"
                        checked={col.getIsVisible()}
                        onChange={(e) => col.toggleVisibility(e.target.checked)}
                      />
                      <span>{label}</span>
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          {/* NEW: Clear sort button */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSorting([]);
              setSort([]);
              setPage(1);
              table.resetSorting();
            }}
          >
            Clear sort
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDeleteSelected}
            disabled={deleting || table.getSelectedRowModel().rows.length === 0}
            className="gap-2 border-red-600 text-red-700 hover:bg-red-50"
            title="Delete selected users"
          >
            <Trash2 className="h-4 w-4" />
            Delete selected ({table.getSelectedRowModel().rows.length || 0})
          </Button>
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
                            onClick={(e) =>
                              header.column.toggleSorting(
                                header.column.getIsSorted() === "asc",
                                e.shiftKey || e.ctrlKey || e.metaKey // NEW
                              )
                            }
                            title="Click to sort; hold Shift/Ctrl/⌘ to multi-sort"
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
