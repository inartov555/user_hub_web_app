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
import { useQuery, useQueryClient, keepPreviousData } from "@tanstack/react-query";
import { Trash2, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Columns, ArrowUpDown } from "lucide-react";
import type { RowSelectionState } from "@tanstack/react-table";
import { api } from "../lib/axios";

import { Button } from "../components/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/card";
import { Input } from "../components/input";
import { Checkbox } from "../components/checkbox";

type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

/**
 * Convert TanStack SortingState -> DRF `ordering` (primary,secondary,...)
 * TanStack keeps highest-priority sort FIRST in `sorting`.
 */
const toOrdering = (s: SortingState) => s.map(({ id, desc }) => (desc ? `-${id}` : id));

/**
 * Always add a deterministic tiebreaker at the end to stabilize pagination.
 * This prevents "random shuffles" when many rows share the same sorted value.
 */
const withStableTiebreaker = (ordering: string[], idField = "id") => {
  if (ordering.some((o) => o === idField || o === `-${idField}`)) return ordering;
  return [...ordering, idField];
};

/**
 * Treat *every* header click as a multi-sort gesture (no Shift/Ctrl needed).
 * This keeps previous sort columns intact instead of resetting them.
 */
const alwaysMulti = () => true;

type Props = {
  data?: User[]; // unused with server pagination
  onResetPasswords?: (userIds: number[]) => Promise<void> | void;
};

export default function UsersTable(props: Props) {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(() => Number(localStorage.getItem("pageSize")) || 20);
  const [globalFilter, setGlobalFilter] = useState("");

  // TanStack state we control
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [showColumns, setShowColumns] = useState(false);
  const [rowSelection, setRowSelection] = React.useState<RowSelectionState>({});

  const queryClient = useQueryClient();
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // Build server ordering param from sorting (with a stable id tiebreaker)
  const ordering = useMemo(
    () => withStableTiebreaker(toOrdering(sorting)),
    [sorting]
  );

  // Data fetch (server-side sort + pagination)
  const { data, isLoading, isFetching } = useQuery<{ results: User[]; count: number }>({
    queryKey: ["users", page, pageSize, ordering, globalFilter],
    placeholderData: keepPreviousData,
    retry: false,
    refetchOnWindowFocus: false,
    queryFn: async ({ signal }) => {
      const params: Record<string, unknown> = { page, page_size: pageSize };
      if (ordering.length) params.ordering = ordering.join(",");
      if (globalFilter) params.search = globalFilter;
      const { data } = await api.get("/users/", { params, signal });
      return data as { results: User[]; count: number };
    },
  });

  const rows = useMemo(() => data?.results ?? [], [data]);
  const totalCount = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  // Columns
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
          onClick={column.getToggleSortingHandler()}
          title="Click to add/update sort (multi-sort enabled)"
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
          onClick={column.getToggleSortingHandler()}
          title="Click to add/update sort (multi-sort enabled)"
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
          onClick={column.getToggleSortingHandler()}
          title="Click to add/update sort (multi-sort enabled)"
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
          onClick={column.getToggleSortingHandler()}
          title="Click to add/update sort (multi-sort enabled)"
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

  // Sync TanStack sorting -> server ordering
  const handleSortingChange = (updater: React.SetStateAction<SortingState>) => {
    const next = typeof updater === "function" ? (updater as (prev: SortingState) => SortingState)(sorting) : updater;
    setSorting(next);
    setPage(1); // whenever sort changes, go back to first page
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
    onSortingChange: handleSortingChange,
    onColumnVisibilityChange: setColumnVisibility,

    getCoreRowModel: getCoreRowModel(),

    // Server-side sorting & pagination
    manualSorting: true,
    manualPagination: true,
    pageCount: totalPages,

    // Multi-sort behavior
    enableMultiSort: true,
    // Always treat clicks as multi-sort; don't require Shift/Ctrl/⌘
    isMultiSortEvent: alwaysMulti,
    // Avoid the "third click removes sorting" behavior (keeps column in sort)
    enableSortingRemoval: false,
    maxMultiSortColCount: 5,

    getPaginationRowModel: getPaginationRowModel(),
    columnResizeMode: "onChange",
    enableColumnResizing: true,
  });

  // persist pageSize
  useEffect(() => {
    localStorage.setItem("pageSize", String(pageSize));
  }, [pageSize]);

  // reset page when size/filter/sort changes
  useEffect(() => {
    table.setPageIndex(0);
    setPage(1);
  }, [pageSize, globalFilter, ordering]); // ordering includes the tiebreaker

  // Bulk delete (unchanged)
  const handleDeleteSelected = async () => {
    const ids = table.getSelectedRowModel().flatRows.map((r) => r.original.id);
    if (!ids.length) return;

    setDeleting(true);
    setDeleteError(null);
    try {
      const bulk = await api.post("/users/bulk-delete/", { ids }, { validateStatus: () => true });

      if (!(bulk.status >= 200 && bulk.status < 300)) {
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

      setRowSelection({});
      await queryClient.invalidateQueries({ queryKey: ["users"] });
    } catch (e: any) {
      setDeleteError(e?.message || "Failed to delete selected users.");
    } finally {
      setDeleting(false);
    }
  };

  if (isLoading && !data) return <div>Loading…</div>;

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

          {/* Columns menu */}
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

          {/* Clear sort */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSorting([]);
              setPage(1);
              table.resetSorting();
            }}
          >
            Clear sort
          </Button>

          {/* Delete selected */}
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
                    const sortIndex = header.column.getSortIndex();
                    return (
                      <th
                        key={header.id}
                        colSpan={header.colSpan}
                        style={{ width: header.getSize() }}
                        className="relative select-none px-3 py-2 text-left font-semibold align-middle group whitespace-normal break-words"
                      >
                        {header.isPlaceholder ? null : (
                          <div className="inline-flex items-center gap-1">
                            {flexRender(header.column.columnDef.header, header.getContext())}
                            {sortIndex > -1 && (
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

        {/* Footer / pagination */}
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
            {isFetching && <span>Updating…</span>}
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

        {deleteError && (
          <div className="mt-3 text-sm text-red-600">{deleteError}</div>
        )}
      </CardContent>
    </Card>
  );
}
