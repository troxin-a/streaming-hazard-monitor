import Stack from '@mui/material/Stack';
import { useState } from 'react';

import { companies, type Company } from '@/entities/company';
import { CompanyFormDialog } from '@/features/companies/CompanyFormDialog';
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog';
import { type Column, DataTable } from '@/shared/ui/DataTable';
import { PageHeader } from '@/shared/ui/PageHeader';
import { RowActions } from '@/shared/ui/RowActions';

const columns: Column<Company>[] = [{ header: 'Название', render: (company) => company.name }];

export function CompaniesPage() {
  const [editing, setEditing] = useState<Company | 'new' | null>(null);
  const [deleting, setDeleting] = useState<Company | null>(null);

  return (
    <Stack spacing={2}>
      <PageHeader title="Компании" onAdd={() => setEditing('new')} />
      <DataTable
        resource={companies}
        columns={columns}
        actions={(company) => (
          <RowActions onEdit={() => setEditing(company)} onDelete={() => setDeleting(company)} />
        )}
      />
      {editing && (
        <CompanyFormDialog
          company={editing === 'new' ? undefined : editing}
          onClose={() => setEditing(null)}
        />
      )}
      {deleting && (
        <ConfirmDialog
          title="Удалить компанию?"
          text={`Компания «${deleting.name}» будет удалена.`}
          action={() => companies.remove(deleting.uuid)}
          onClose={() => setDeleting(null)}
        />
      )}
    </Stack>
  );
}
