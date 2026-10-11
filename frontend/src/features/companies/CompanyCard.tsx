import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import Button from '@mui/material/Button';
import { useState } from 'react';

import { companies, type Company } from '@/entities/company';
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog';
import type { Column } from '@/shared/ui/DataTable';
import { RecordCard } from '@/shared/ui/RecordCard';

import { CompanyFormDialog } from './CompanyFormDialog';

interface CompanyCardProps {
  company: Company;
  columns: Column<Company>[];
  onClose: () => void;
}

/** Карточка компании с действиями над ней. */
export function CompanyCard({ company, columns, onClose }: CompanyCardProps) {
  const [editing, setEditing] = useState(false);
  const [deleting, setDeleting] = useState(false);

  return (
    <>
      <RecordCard
        title={company.name}
        row={company}
        columns={columns}
        onClose={onClose}
        view={editing && <CompanyFormDialog company={company} onClose={() => setEditing(false)} />}
      >
        <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setEditing(true)}>
          Изменить
        </Button>
        <Button
          variant="outlined"
          color="error"
          startIcon={<DeleteIcon />}
          onClick={() => setDeleting(true)}
        >
          Удалить
        </Button>
      </RecordCard>
      {deleting && (
        <ConfirmDialog
          title="Удалить компанию?"
          text={`Компания «${company.name}» будет удалена.`}
          action={() => companies.remove(company.uuid)}
          successMessage="Компания удалена"
          onClose={() => setDeleting(false)}
        />
      )}
    </>
  );
}
