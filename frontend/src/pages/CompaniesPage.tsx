import Stack from '@mui/material/Stack';
import { useState } from 'react';

import { companies, type Company } from '@/entities/company';
import { CompanyCard } from '@/features/companies/CompanyCard';
import { CompanyFormDialog } from '@/features/companies/CompanyFormDialog';
import { type Column, DataTable } from '@/shared/ui/DataTable';
import { PageHeader } from '@/shared/ui/PageHeader';

const columns: Column<Company>[] = [{ header: 'Название', render: (company) => company.name }];

export function CompaniesPage() {
  const [creating, setCreating] = useState(false);

  return (
    <Stack spacing={2}>
      <PageHeader title="Компании" onAdd={() => setCreating(true)} />
      <DataTable
        resource={companies}
        columns={columns}
        searchLabel="Поиск по названию"
        card={(company, onClose) => (
          <CompanyCard company={company} columns={columns} onClose={onClose} />
        )}
      />
      {creating && <CompanyFormDialog onClose={() => setCreating(false)} />}
    </Stack>
  );
}
