import * as React from 'react';
import api from '../lib/api';
import { DataTable } from '../components/table/DataTable';
import { ColumnDef } from '@tanstack/react-table';

type User = {
  id: number; username: string; email: string; first_name: string; last_name: string; title: string; avatar?: string;
}

export default function Users() {
  const [data, setData] = React.useState<User[]>([]);
  const [total, setTotal] = React.useState(0);
  const [page, setPage] = React.useState(0);
  const [pageSize, setPageSize] = React.useState(20);
  const [sorting, setSorting] = React.useState<{id: string; desc: boolean}[]>([]);

  const fetchData = React.useCallback(async () => {
    const order = sorting.map(s => (s.desc ? '-' : '') + s.id);
    const { data } = await api.get('/users/', {
      params: { limit: pageSize, offset: page * pageSize, sort: order }
    });
    setData(data.results);
    setTotal(data.count);
  }, [page, pageSize, sorting]);

  React.useEffect(() => { fetchData(); }, [fetchData]);

  const columns: ColumnDef<User>[] = [
    { accessorKey: 'id', header: 'ID' },
    { accessorKey: 'username', header: 'Username' },
    { accessorKey: 'email', header: 'Email' },
    { accessorKey: 'first_name', header: 'First name' },
    { accessorKey: 'last_name', header: 'Last name' },
    { accessorKey: 'title', header: 'Title' },
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">All Users</h1>
      <DataTable
        columns={columns}
        data={data}
        page={page}
        pageSize={pageSize}
        total={total}
        onPageChange={setPage}
        onPageSizeChange={(n) => { setPage(0); setPageSize(n); }}
        onSortChange={(s) => setSorting(s.map(x => ({ id: x.id!, desc: x.desc ?? false })))}
      />
    </div>
  );
}
