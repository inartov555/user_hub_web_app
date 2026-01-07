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
  Trash2, FilterX, Users,
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
 * Convert TanStack SortingState -> DRF ordering (primary,secondary,...)
 * TanStack keeps highest-priority sort FIRST in sorting.
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
 * Treat every header click as a multi-sort gesture (no Shift/Ctrl needed).
 * This keeps previous sort columns intact instead of resetting them.
 */
const alwaysMulti = () => true;

const readColumnVisibility = (): VisibilityState | null => {
  try {
    if (typeof window === "undefined") return null;
    const raw = localStorage.getItem("usersTable.columnVisibility");
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    return parsed as VisibilityState;
  } catch {
    return null;
  }
};
const defaultColumnVisibility = (isAdmin: boolean): VisibilityState =>
  isAdmin ? {} : { select: false, change_password_action: false };
const normalizeColumnVisibility = (vis: VisibilityState, isAdmin: boolean): VisibilityState => {
  const next: VisibilityState = { ...vis };

  if (isAdmin) {
    // these are admin-only and are marked enableHiding: false -> never allow hidden state
    delete next.select;
    delete next.change_password_action;
  } else {
    // non-admin must never see these even if localStorage was polluted
    next.select = false;
    next.change_password_action = false;
  }

  return next;
};

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
  const [pageSize, setPageSize] = useState<number>(() => Number(localStorage.getItem("pageSize")) || 5);
  const [globalFilter, setGlobalFilter] = useState("");

  const [sorting, setSorting] = useState<SortingState>(() => {
    try {
      const raw = localStorage.getItem("usersTable.sorting");
      return raw ? (JSON.parse(raw) as SortingState) : [];
    } catch {
      return [];
    }
  });

  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(() => {
    const stored = readColumnVisibility();
    return normalizeColumnVisibility(stored ?? defaultColumnVisibility(isAdmin), isAdmin);
  });
  useEffect(() => {
    const stored = readColumnVisibility();
    setColumnVisibility(normalizeColumnVisibility(stored ?? defaultColumnVisibility(isAdmin), isAdmin));
  }, [isAdmin]);
  const [showColumns, setShowColumns] = useState(false);
  const [rowSelection, setRowSelection] = React.useState<RowSelectionState>({});

  const columnsMenuContainerRef = React.useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!showColumns) return;

    const onPointerDown = (e: MouseEvent | TouchEvent) => {
      const el = columnsMenuContainerRef.current;
      const target = e.target as Node | null;
      if (!el || !target) return;

      if (!el.contains(target)) setShowColumns(false);
    };

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setShowColumns(false);
    };

    document.addEventListener("mousedown", onPointerDown, true);
    document.addEventListener("touchstart", onPointerDown, true);
    document.addEventListener("keydown", onKeyDown, true);

    return () => {
      document.removeEventListener("mousedown", onPointerDown, true);
      document.removeEventListener("touchstart", onPointerDown, true);
      document.removeEventListener("keydown", onKeyDown, true);
    };
  }, [showColumns]);

  // put inside UsersTable, above columns
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

  const onSortHeaderClick =
  (column: any) => (e: React.MouseEvent<HTMLButtonElement>) => {
    // run TanStack default behavior
    column.getToggleSortingHandler()?.(e);

    // persist the next state (after React processes the update)
    setTimeout(() => {
      const next = table.getState().sorting;
      localStorage.setItem("usersTable.sorting", JSON.stringify(next));
    }, 0);
  };

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
          <div className="px-2 w-full justify-center">
            <Checkbox
              data-tag="check-all-rows"
              checked={all}
              indeterminate={!all && some}
              onChange={(e) => table.toggleAllRowsSelected(e.currentTarget.checked)}
              aria-label="Select all"
              className={headerButtonClassName(undefined)}
            />
          </div>
        );
      },
      cell: ({ row }) => (
        <div className="px-2 w-full justify-center">
          <Checkbox
            data-tag="check-a-row"
            checked={row.getIsSelected()}
            indeterminate={row.getIsSomeSelected()}
            onChange={(e) => row.toggleSelected(e.currentTarget.checked)}
            aria-label="Select row"
            className={headerButtonClassName(undefined)}
          />
        </div>
      ),
      size: 30,
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
          className={headerButtonClassName(Boolean(column.getIsSorted()))}
          onClick={onSortHeaderClick(column)}
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
          className={headerButtonClassName(Boolean(column.getIsSorted()))}
          onClick={onSortHeaderClick(column)}
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
          className={headerButtonClassName(Boolean(column.getIsSorted()))}
          onClick={onSortHeaderClick(column)}
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
          className={headerButtonClassName(Boolean(column.getIsSorted()))}
          onClick={onSortHeaderClick(column)}
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
      header: () => (<div data-tag="changePasswordHeader"
                          className="inline-flex items-center gap-1 w-full justify-center"
                     >
                       <span>{t("users.changePassword")}</span>
                     </div>),
      size: 205,
      enableSorting: false,
      cell: ({ row }) => (
        <div className={headerButtonClassName(undefined)}>
          <Button
            data-tag="change-password"
            onClick={() => navigate(`/users/${row.original.id}/change-password`)}
            title={t("users.changePassword")}
          >
            {t("users.changePassword")}
          </Button>
        </div>
      ),
    }] : []),
  ], [navigate, isAdmin, i18n.resolvedLanguage]);

  const headerButtonClassName = (sorted: boolean) =>
    [
      "relative inline-flex items-center gap-2 rounded-xl px-2.5 py-1.5 -ml-2",
      "font-semibold tracking-[0.01em]",
      "transition-all duration-150",
      "active:bg-slate-200/80 dark:active:bg-slate-700/70",
      "active:translate-y-[0.5px]",
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500/35 focus-visible:ring-offset-2",
      "focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900",
      "after:absolute after:left-3 after:right-3 after:-bottom-1 after:h-[2px] after:rounded-full after:bg-red-500/60",
      "after:opacity-0 after:transition-opacity",
      sorted && "text-slate-900 dark:text-slate-50 after:opacity-100 w-full justify-center",
      !sorted && "text-slate-700 dark:text-slate-200"
    ].join(" ");

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
    enableSortingRemoval: true,
    maxMultiSortColCount: 5,

    getPaginationRowModel: getPaginationRowModel(),
    columnResizeMode: "onChange",
    enableColumnResizing: true,
  });

  const visibleLeafColumnCount = table.getVisibleLeafColumns().length;

  // persist pageSize
  useEffect(() => {
    localStorage.setItem("pageSize", String(pageSize));
  }, [pageSize]);

  // reset page when size/filter/sort changes
  useEffect(() => {
    table.setPageIndex(0);
    setPage(1);
  }, [pageSize, globalFilter, ordering]); // ordering includes the tiebreaker

  useEffect(() => {
    try {
      const normalized = normalizeColumnVisibility(columnVisibility, isAdmin);
      localStorage.setItem("usersTable.columnVisibility", JSON.stringify(normalized));
    } catch {
      // ignore
    }
  }, [columnVisibility, isAdmin]);

  /** Navigate to confirmation page instead of deleting immediately */
  const handleGoToDeleteConfirm = () => {
    const selectedUsers = table.getSelectedRowModel().flatRows.map((r) => r.original as User);
    if (!selectedUsers.length) return;
    navigate("/users/confirm-delete", { state: { users: selectedUsers } });
  };

  if (isLoading && !data) return <div>{t("users.loading")}</div>;

  return (
    <Card className="
            relative overflow-hidden rounded-2xl border p-4
            bg-white/75 backdrop-blur shadow-soft ring-1 ring-slate-900/5
            dark:bg-slate-900/50 dark:border-slate-700/70 dark:text-slate-100 dark:ring-white/5
          "
    >
      <div aria-hidden
           className="
             pointer-events-none absolute inset-x-0 top-0 h-24
             bg-gradient-to-b from-brand-500/10 via-indigo-500/6 to-transparent
             dark:from-brand-400/12 dark:via-indigo-400/8
           "
      />
      <CardHeader icon=<Users className="h-4 w-4" /> title={`${t("users.people")} (${totalCount})`} />
      <CardBody className="justify-end mt-2">
        <div className="flex w-full items-center justify-end gap-2">
          <Input
            id="search"
            className={`max-w-[360px]`}
            placeholder={t("users.search")}
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            maxLength={40}
          />

          {/* Column visibility button */}
          <div className="relative" ref={columnsMenuContainerRef}>
            <Button id="columnVisibility" onClick={() => setShowColumns((v) => !v)}>
              <Columns className="h-4 w-4" /> {t("users.columns")}
            </Button>
            {showColumns && (
              <div
                data-tag="columnVisibilityPopup"
                className="
                  absolute right-0 z-50 mt-2 w-56 rounded-md border bg-white p-2 shadow-lg dark:bg-slate-900
                  dark:text-slate-100 dark:placeholder-slate-500 dark:border-slate-700
                "
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
                      <label data-tag={col.id}
                             key={col.id}
                             className="
                               flex cursor-pointer items-center gap-2 rounded px-2 py-1.5
                               hover:bg-slate-200/70 dark:hover:bg-slate-200/80 dark:hover:text-slate-900
                             "
                      >
                        <input
                          type="checkbox"
                          checked={col.getIsVisible()}
                          onChange={(e) => col.toggleVisibility(e.target.checked)}
                        />
                        <span>{label}</span>
                      </label>
                    );
                  })
                }
              </div>
            )}
          </div>

          {/* Clear sort button */}
          <Button
            id="clearSort"
            onClick={() => {
              setSorting([]);
              setPage(1);
              table.resetSorting();
              localStorage.setItem("usersTable.sorting", undefined);
            }}
          >
            <FilterX className="h-4 w-4" />
            {t("users.clearSort")}
          </Button>

          {/* Delete selected button (admin only) */}
          {isAdmin && (
            <Button
              id="deleteUsers"
              onClick={handleGoToDeleteConfirm}
              disabled={table.getSelectedRowModel().rows.length === 0}
              title={t("users.deleteSelectedTitle")}
            >
              <Trash2 className="h-4 w-4" />
              {t("users.deleteSelected")} ({table.getSelectedRowModel().rows.length || 0})
            </Button>

          )}
        </div>
      </CardBody>

      <CardBody>
        {visibleLeafColumnCount === 0 ? (
          <div className="rounded-xl border p-8 text-center">
            <p
              data-tag="noVisibleColumnsHint"
              className="text-sm text-slate-600 dark:text-slate-200"
            >
              {t("users.noVisibleColumns")}
            </p>
          </div>
        ) : (
          <>
            {/* Top / pagination */}
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Button
                  id="toFirstPageTop"
                  title={t("users.firstPage")}
                  onClick={() => (table.setPageIndex(0), setPage(1))}
                  disabled={!table.getCanPreviousPage()}
                >
                  <ChevronsLeft className="h-4 w-4" />
                </Button>
                <Button
                  id="toPreviousPageTop"
                  title={t("users.previousPage")}
                  onClick={() => (table.previousPage(), setPage((p) => Math.max(1, p - 1)))}
                  disabled={!table.getCanPreviousPage()}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  id="toNextPageTop"
                  title={t("users.nextPage")}
                  onClick={() => (table.nextPage(), setPage((p) => p + 1))}
                  disabled={!table.getCanNextPage()}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
                <Button
                  id="toLastPageTop"
                  title={t("users.lastPage")}
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

              <div data-tag="paginationTop" className="flex items-center gap-3 text-sm text-muted-foreground">
                {isFetching && <span data-tag="isUpdatingTop">{t("users.updating")}</span>}
                <span data-tag="pageOfPagesTop">
                  {t("users.page")} <strong>{table.getState().pagination.pageIndex + 1}</strong> {t("users.of")}{" "}
                  {table.getPageCount() || 1}
                </span>
                <label className="flex items-center gap-2">
                  {t("users.rowsPerPage")}
                  <select
                    id="rowsPerPageTop"
                    className="
                      border border-slate-300 dark:border-slate-700 rounded bg-white dark:bg-slate-900 px-2 py-1 text-sm
                      text-slate-900 dark:text-slate-100 dark:[color-scheme:dark]
                      dark:[&>option]:bg-slate-900 dark:[&>option]:text-slate-100
                    "
                    value={table.getState().pagination.pageSize}
                    onChange={(e) => {
                      const ps = Number(e.target.value);
                      table.setPageSize(ps);
                      setPageSize(ps);
                    }}
                  >
                    {[5, 10, 20, 30, 50, 100, 200, 500, 1000, 2000].map((ps) => (
                      <option key={ps} value={ps}>
                        {ps}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </div>

            {/* The users table */}
            <div className="overflow-auto rounded-xl border">
              <table className="w-full text-sm table-auto border-collapse">
                <thead className="bg-muted/50">
                  {table.getHeaderGroups().map((headerGroup) => (
                    <tr key={headerGroup.id}
                        className="
                          divide-x divide-slate-300 dark:divide-slate-600 border-b border-slate-300
                          dark:border-slate-600
                        "
                    >
                      {headerGroup.headers.map((header) => {
                        const sortIndex = header.column.getSortIndex();
                        return (
                          <th
                            key={header.id}
                            colSpan={header.colSpan}
                            style={{ width: header.getSize() }}
                            className="
                              group bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                              relative select-none px-3 py-2 text-left font-semibold align-middle
                              whitespace-normal break-words w-full justify-center
                              hover:bg-slate-400/80 dark:hover:bg-slate-400/80 dark:hover:text-slate-100
                            "
                          >
                            {header.isPlaceholder ? null : (
                              <div className="inline-flex items-center gap-1 w-full justify-center">
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
                        {t("users.noSearchResults")}
                      </td>
                    </tr>
                  ) : (
                    table.getRowModel().rows.map((row) => (
                      <tr key={row.id}
                          data-tag={"row-userId-" + row.id}
                          className={[
                            "border-b divide-x divide-slate-300 dark:divide-slate-600",
                            "hover:bg-slate-200/70 dark:hover:bg-slate-200/80 dark:hover:text-slate-900",
                            // Persistent highlight when checked/selected
                            row.getIsSelected() && "bg-slate-200/70 dark:bg-slate-200/80 dark:text-slate-900",
                            // Also keep highlight when any control inside has focus
                            row.getIsSelected() && "focus-within:bg-slate-200/70 dark:focus-within:bg-slate-200/80 dark:focus-within:text-slate-900",
                            "hover:bg-slate-400/80 dark:hover:bg-slate-400/80 dark:hover:text-slate-100",
                          ].filter(Boolean).join(" ")}
                      >
                        {row.getVisibleCells().map((cell, cellIndex) => (
                          <td
                            key={cell.id}
                            data-tag={"cell-" + cellIndex}
                            style={{ width: cell.column.getSize(), overflowWrap: "anywhere", wordBreak: "break-word", whiteSpace: "pre-wrap" }}
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
                  id="toFirstPageBottom"
                  title={t("users.firstPage")}
                  onClick={() => (table.setPageIndex(0), setPage(1))}
                  disabled={!table.getCanPreviousPage()}
                >
                  <ChevronsLeft className="h-4 w-4" />
                </Button>
                <Button
                  id="toPreviousPageBottom"
                  title={t("users.previousPage")}
                  onClick={() => (table.previousPage(), setPage((p) => Math.max(1, p - 1)))}
                  disabled={!table.getCanPreviousPage()}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  id="toNextPageBottom"
                  title={t("users.nextPage")}
                  onClick={() => (table.nextPage(), setPage((p) => p + 1))}
                  disabled={!table.getCanNextPage()}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
                <Button
                  id="toLastPageBottom"
                  title={t("users.lastPage")}
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

              <div data-tag="paginationBottom" className="flex items-center gap-3 text-sm text-muted-foreground">
                {isFetching && <span data-tag="isUpdatingBottom">{t("users.updating")}</span>}
                <span data-tag="pageOfPagesBottom">
                  {t("users.page")} <strong>{table.getState().pagination.pageIndex + 1}</strong> {t("users.of")}{" "}
                  {table.getPageCount() || 1}
                </span>
                <label className="flex items-center gap-2">
                  {t("users.rowsPerPage")}
                  <select
                    id="rowsPerPageBottom"
                    className="
                      border border-slate-300 dark:border-slate-700 rounded bg-white dark:bg-slate-900 px-2 py-1 text-sm
                      text-slate-900 dark:text-slate-100 dark:[color-scheme:dark]
                      dark:[&>option]:bg-slate-900 dark:[&>option]:text-slate-100
                    "
                    value={table.getState().pagination.pageSize}
                    onChange={(e) => {
                      const ps = Number(e.target.value);
                      table.setPageSize(ps);
                      setPageSize(ps);
                    }}
                  >
                    {[5, 10, 20, 30, 50, 100, 200, 500, 1000, 2000].map((ps) => (
                      <option key={ps} value={ps}>
                        {ps}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </div>
          </>
        )}
      </CardBody>
    </Card>
  );
}
