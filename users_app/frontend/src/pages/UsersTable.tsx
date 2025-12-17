import * as React from "react";
import { useMemo, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
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
import {
  Trash2,
  ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight,
  Columns, ArrowUpDown, ArrowUp, ArrowDown
} from "lucide-react";
import type { RowSelectionState } from "@tanstack/react-table";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";
import Button from "../components/button";
import { Card, CardBody, CardHeader } from "../components/card";
import { Input } from "../components/input";
import { Checkbox } from "../components/checkbox";

type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

type AdminFlags = {
  is_admin?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
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
  const { t, i18n } = useTranslation();
  const cur_user = useAuthStore((s) => s.user) as (User & AdminFlags) | null | undefined;
  const isAdmin = Boolean(cur_user?.is_admin || cur_user?.is_staff || cur_user?.is_superuser);
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(() => Number(localStorage.getItem("pageSize")) || 20);
  const [globalFilter, setGlobalFilter] = useState("");

  // TanStack state we control
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(() =>
    isAdmin ? {} : { select: false, change_password_action: false }
  );
  const [showColumns, setShowColumns] = useState(false);
  const [rowSelection, setRowSelection] = React.useState<RowSelectionState>({});
  // put inside UsersTable, above `columns`
  const sortLabel = (column: any): string | undefined => {
    const dir = column.getIsSorted() as 'asc' | 'desc' | false;
    if (!dir) return undefined;
    const map = {
      asc: t('users.ascending'),
      desc: t('users.descending'),
    } satisfies Record<'asc' | 'desc', string>;
    return map[dir];
  };
  const SortIcon = ({ column }: { column: any }) => {
    const get_sorted_order = column.getIsSorted(); // 'asc' | 'desc' | false
    if (get_sorted_order === "asc") return <ArrowUp className="h-4 w-4" aria-label="sorted ascending" />;
    if (get_sorted_order === "desc") return <ArrowDown className="h-4 w-4" aria-label="sorted descending" />;
    return <ArrowUpDown className="h-4 w-4 opacity-40" aria-label="not sorted" />;
  };

  const queryClient = useQueryClient();

  // Build server-side ordering tokens from TanStack sorting, with stable tiebreaker
  const ordering = React.useMemo(
    () => withStableTiebreaker(toOrdering(sorting), "id"),
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
    ...(isAdmin ? [{
      accessorKey: "select",
      meta: { i18nKey: "users.select" },
      enableHiding: false,
      header: ({ table }) => {
        const all = table.getIsAllRowsSelected();
        const some = table.getIsSomeRowsSelected();
        return (
          <div className="px-2">
            <Checkbox
              data-tag="check-all-rows"
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
            data-tag="check-a-row"
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
    }] : []),
    {
      accessorKey: "username",
      meta: { i18nKey: "signup.username" },
      header: ({ column }) => (
        <button
          type="button"
          data-tag="sort-by-username"
          className="inline-flex items-center gap-1"
          onClick={column.getToggleSortingHandler()}
          title={
            column.getIsSorted()
            ? `${t("users.sorted")} ${sortLabel(column)} (#${column.getSortIndex() + 1})`
            : t("users.clickToSort")
          }
        >
          {t("signup.username")} <SortIcon column={column} />
        </button>
      ),
      cell: (info) => <span className="font-medium break-words">{info.getValue() as string}</span>,
      size: 220,
      enableResizing: true,
    },
    {
      accessorKey: "email",
      meta: { i18nKey: "signup.email" },
      header: ({ column }) => (
        <button
          type="button"
          data-tag="sort-by-email"
          className="inline-flex items-center gap-1"
          onClick={column.getToggleSortingHandler()}
          title={
            column.getIsSorted()
            ? `${t("users.sorted")} ${sortLabel(column)} (#${column.getSortIndex() + 1})`
            : t("users.clickToSort")
          }
        >
          {t("signup.email")} <SortIcon column={column} />
        </button>
      ),
      cell: (ctx) => <span className="break-words">{ctx.getValue<string>()}</span>,
      size: 280,
      enableResizing: true,
    },
    {
      accessorKey: "first_name",
      meta: { i18nKey: "users.firstName" },
      header: ({ column }) => (
        <button
          type="button"
          data-tag="sort-by-firstname"
          className="inline-flex items-center gap-1"
          onClick={column.getToggleSortingHandler()}
          title={
            column.getIsSorted()
            ? `${t("users.sorted")} ${sortLabel(column)} (#${column.getSortIndex() + 1})`
            : t("users.clickToSort")
          }
        >
          {t("users.firstName")} <SortIcon column={column} />
        </button>
      ),
      cell: (ctx) => <span className="break-words">{ctx.getValue<string>()}</span>,
      size: 180,
      enableResizing: true,
    },
    {
      accessorKey: "last_name",
      meta: { i18nKey: "users.lastName" },
      header: ({ column }) => (
        <button
          type="button"
          data-tag="sort-by-lastname"
          className="inline-flex items-center gap-1"
          onClick={column.getToggleSortingHandler()}
          title={
            column.getIsSorted()
            ? `${t("users.sorted")} ${sortLabel(column)} (#${column.getSortIndex() + 1})`
            : t("users.clickToSort")
          }
        >
          {t("users.lastName")} <SortIcon column={column} />
        </button>
      ),
      cell: (ctx) => <span className="break-words">{ctx.getValue<string>()}</span>,
      size: 180,
      enableResizing: true,
    },
    ...(isAdmin ? [{
      accessorKey: "change_password_action",
      meta: { i18nKey: "users.changePassword" },
      enableHiding: false,
      header: () => (<div data-tag="changePasswordHeader">{t("users.changePassword")}</div>),
      enableSorting: false,
      size: 180,
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-2">
          <Button
            data-tag="change-password"
            variant="secondary"
            onClick={() => navigate(`/users/${row.original.id}/change-password`)}
            title={t("users.changePassword")}
          >
            {t("users.changePassword")}
          </Button>
        </div>
      ),
    }] : []),
  ], [navigate, isAdmin, i18n.resolvedLanguage]);

  // Sync TanStack sorting - server ordering
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
    // Stable selection across pages & admin-only selection
    getRowId: (row) => String(row.id),
    onRowSelectionChange: setRowSelection,
    enableRowSelection: isAdmin,
    onSortingChange: handleSortingChange,
    onColumnVisibilityChange: setColumnVisibility,

    getCoreRowModel: getCoreRowModel(),

    // Server-side sorting & pagination
    manualSorting: true,
    manualPagination: true,
    pageCount: totalPages,

    // Multi-sort behavior
    enableMultiSort: true,
    // Always treat clicks as multi-sort; don't require Shift/Ctrl
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

  /** Navigate to confirmation page instead of deleting immediately */
  const handleGoToDeleteConfirm = () => {
    const selectedUsers = table.getSelectedRowModel().flatRows.map((r) => r.original as User);
    if (!selectedUsers.length) return;
    navigate("/users/confirm-delete", { state: { users: selectedUsers } });
  };

  if (isLoading && !data) return <div>{t("users.loading")}</div>;

  return (
    <Card className="w-full mx-auto dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <CardHeader title={t("users.people")} />
      <CardBody className="flex justify-end mt-2">
        <div className="flex items-center gap-2">
          <Input
            id="search"
            placeholder={t("users.search")}
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="w-48 dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700"
          />

          {/* Columns menu */}
          <div className="relative">
            <Button id="columnVisibility" variant="secondary" className="gap-2" onClick={() => setShowColumns((v) => !v)}>
              <Columns className="h-4 w-4" /> {t("users.columns")}
            </Button>
            {showColumns && (
              <div
                className="absolute right-0 z-10 mt-2 w-56 rounded-md border bg-white p-2 shadow-lg dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
                  dark:border-slate-700"
                role="menu"
              >
                <div className="px-2 py-1 text-xs font-medium text-slate-500">{t("users.toggleColumns")}</div>
                <div className="my-2 h-px bg-slate-200" />
                {table
                  .getAllLeafColumns()
                  .filter((col) => col.columnDef.enableHiding !== false)
                  .map((col) => {
                  const accessorKey = typeof col.columnDef.header === "string" ? col.columnDef.header : col.id;
                  // Safely derive a localized string
                  const meta = col.columnDef.meta as { label?: string; i18nKey?: string } | undefined;
                  const label =
                    meta?.label ??
                    (meta?.i18nKey ? t(meta.i18nKey) : undefined);
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
            id="clearSort"
            variant="secondary"
            onClick={() => {
              setSorting([]);
              setPage(1);
              table.resetSorting();
            }}
          >
            {t("users.clearSort")}
          </Button>

          {/* Delete selected (admin only) */}
          {isAdmin && (
            <Button
              id="deleteUsers"
              variant="secondary"
              onClick={handleGoToDeleteConfirm}
              disabled={table.getSelectedRowModel().rows.length === 0}
              className="gap-2 border-red-600 text-red-700 hover:bg-red-50"
              title={t("users.deleteSelectedTitle")}
            >
              <Trash2 className="h-4 w-4" />
              {t("users.deleteSelected")} ({table.getSelectedRowModel().rows.length || 0})
            </Button>

          )}
        </div>
      </CardBody>

      <CardBody>
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
                  <tr data-tag={"row-" + row.id} key={row.id} className="border-b hover:bg-muted/40">
                    {row.getVisibleCells().map((cell, cellIndex) => (
                      <td
                        key={cell.id}
                        data-tag={"cell-" + cellIndex}
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
              variant="secondary"
              onClick={() => (table.setPageIndex(0), setPage(1))}
              disabled={!table.getCanPreviousPage()}
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
              onClick={() => (table.previousPage(), setPage((p) => Math.max(1, p - 1)))}
              disabled={!table.getCanPreviousPage()}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
              onClick={() => (table.nextPage(), setPage((p) => p + 1))}
              disabled={!table.getCanNextPage()}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
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
            {isFetching && <span data-tag="isUpdating">{t("users.updating")}</span>}
            <span>
              {t("users.page")} <strong>{table.getState().pagination.pageIndex + 1}</strong> {t("users.of")} {table.getPageCount() || 1}
            </span>
            <label className="flex items-center gap-2">
              {t("users.rowsPerPage")}
              <select
                className="rounded-md border bg-background px-2 py-1 dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
                  dark:border-slate-700"
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
      </CardBody>
    </Card>
  );
}
