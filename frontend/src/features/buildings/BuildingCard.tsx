import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import Button from '@mui/material/Button';
import { useState } from 'react';

import { type Building, buildings } from '@/entities/building';
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog';
import type { Column } from '@/shared/ui/DataTable';
import { RecordCard } from '@/shared/ui/RecordCard';

import { BuildingFormDialog } from './BuildingFormDialog';

interface BuildingCardProps {
  building: Building;
  columns: Column<Building>[];
  onClose: () => void;
}

/** Карточка здания с действиями над ним. */
export function BuildingCard({ building, columns, onClose }: BuildingCardProps) {
  const [editing, setEditing] = useState(false);
  const [deleting, setDeleting] = useState(false);

  return (
    <>
      <RecordCard
        title={building.name}
        row={building}
        columns={columns}
        onClose={onClose}
        view={
          editing && <BuildingFormDialog building={building} onClose={() => setEditing(false)} />
        }
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
          title="Удалить здание?"
          text={`Здание «${building.name}» будет удалено.`}
          action={() => buildings.remove(building.uuid)}
          successMessage="Здание удалено"
          onClose={() => setDeleting(false)}
        />
      )}
    </>
  );
}
