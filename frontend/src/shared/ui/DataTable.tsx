import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import LinearProgress from '@mui/material/LinearProgress';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import { type ReactNode, useState } from 'react';

import { getErrorMessage } from '@/shared/api/client';
import { useResourcePage } from '@/shared/api/hooks';
import type { Listable } from '@/shared/api/resource';

const PAGE_SIZES = [10, 25, 50];

export interface Column<T> {
  header: string;
  render: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  resource: Listable<T>;
  columns: Column<T>[];
  /** Кнопки действий над строкой; без них колонка действий не показывается. */
  actions?: (row: T) => ReactNode;
}

/** Таблица записей сущности с постраничной загрузкой. */
export function DataTable<T extends { uuid: string }>({
  resource,
  columns,
  actions,
}: DataTableProps<T>) {
  const [page, setPage] = useState(0);
  const [size, setSize] = useState(PAGE_SIZES[0]);
  const { data, isPending, isError, error, isFetching, refetch } = useResourcePage(resource, {
    page: page + 1,
    size,
  });

  if (isPending) {
    return <LinearProgress aria-label="Загрузка" />;
  }

  if (isError) {
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={() => refetch()}>
            Повторить
          </Button>
        }
      >
        {getErrorMessage(error)}
      </Alert>
    );
  }

  // После удаления последней записи на странице возвращаемся на существующую.
  const lastPage = Math.max(0, data.pages - 1);
  if (page > lastPage) {
    setPage(lastPage);
  }

  const columnCount = columns.length + (actions ? 1 : 0);

  return (
    <Paper variant="outlined">
      <LinearProgress sx={{ visibility: isFetching ? 'visible' : 'hidden' }} aria-hidden />
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell key={column.header}>{column.header}</TableCell>
              ))}
              {actions && <TableCell align="right">Действия</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.items.map((row) => (
              <TableRow key={row.uuid} hover>
                {columns.map((column) => (
                  <TableCell key={column.header}>{column.render(row)}</TableCell>
                ))}
                {actions && (
                  <TableCell align="right" sx={{ whiteSpace: 'nowrap' }}>
                    {actions(row)}
                  </TableCell>
                )}
              </TableRow>
            ))}
            {data.items.length === 0 && (
              <TableRow>
                <TableCell colSpan={columnCount} align="center" sx={{ color: 'text.secondary' }}>
                  Записей нет
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        component="div"
        count={data.total}
        page={Math.min(page, lastPage)}
        rowsPerPage={size}
        rowsPerPageOptions={PAGE_SIZES}
        onPageChange={(_, nextPage) => setPage(nextPage)}
        onRowsPerPageChange={(event) => {
          setSize(Number(event.target.value));
          setPage(0);
        }}
      />
    </Paper>
  );
}
