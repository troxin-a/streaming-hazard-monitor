import SearchIcon from '@mui/icons-material/Search';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TextField from '@mui/material/TextField';
import { type KeyboardEvent, type ReactNode, useState } from 'react';

import { getErrorMessage } from '@/shared/api/client';
import { useResourcePage } from '@/shared/api/hooks';
import type { Listable } from '@/shared/api/resource';
import { useDebouncedValue } from '@/shared/lib/useDebouncedValue';

const PAGE_SIZES = [10, 25, 50];
/** Высота заглушки на время первой загрузки, примерно как у таблицы с несколькими строками. */
const SKELETON_HEIGHT = 280;

export interface Column<T> {
  header: string;
  render: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  resource: Listable<T>;
  columns: Column<T>[];
  /** Карточка записи, которая открывается по клику на строку; без неё строки не нажимаются. */
  card?: (row: T, onClose: () => void) => ReactNode;
  /** Подпись поля поиска, например «Поиск по названию». */
  searchLabel: string;
}

/** Таблица записей сущности с поиском и постраничной загрузкой. */
export function DataTable<T extends { uuid: string }>({
  resource,
  columns,
  card,
  searchLabel,
}: DataTableProps<T>) {
  const [openedUuid, setOpenedUuid] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [size, setSize] = useState(PAGE_SIZES[0]);
  const [searchText, setSearchText] = useState('');
  const search = useDebouncedValue(searchText.trim());
  const { data, isPending, isError, error, refetch } = useResourcePage(resource, {
    page: page + 1,
    size,
    search,
  });

  if (isPending) {
    return <Skeleton variant="rounded" height={SKELETON_HEIGHT} aria-label="Загрузка" />;
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

  // Запись берётся из загруженной страницы, поэтому карточка показывает данные после правки
  // и пропадает вместе с удалённой записью.
  const opened = data.items.find((row) => row.uuid === openedUuid);

  return (
    <Paper variant="outlined">
      <TextField
        label={searchLabel}
        type="search"
        size="small"
        value={searchText}
        onChange={(event) => {
          setSearchText(event.target.value);
          setPage(0);
        }}
        sx={{ m: 2, width: { xs: 'calc(100% - 32px)', sm: 320 } }}
        slotProps={{
          input: {
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          },
        }}
      />
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell key={column.header}>{column.header}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.items.map((row) => (
              <TableRow
                key={row.uuid}
                hover
                {...(card && {
                  tabIndex: 0,
                  sx: { cursor: 'pointer' },
                  onClick: () => setOpenedUuid(row.uuid),
                  onKeyDown: (event: KeyboardEvent) => {
                    if (event.key === 'Enter') {
                      setOpenedUuid(row.uuid);
                    }
                  },
                })}
              >
                {columns.map((column) => (
                  <TableCell key={column.header}>{column.render(row)}</TableCell>
                ))}
              </TableRow>
            ))}
            {data.items.length === 0 && (
              <TableRow>
                <TableCell colSpan={columns.length} align="center" sx={{ color: 'text.secondary' }}>
                  {search ? 'Ничего не найдено' : 'Записей нет'}
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
      {card && opened && card(opened, () => setOpenedUuid(null))}
    </Paper>
  );
}
