import { zodResolver } from '@hookform/resolvers/zod';
import TextField from '@mui/material/TextField';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { companies, type Company } from '@/entities/company';
import { useResourceMutation } from '@/shared/api/hooks';
import { errorProps } from '@/shared/ui/form';
import { FormDialog } from '@/shared/ui/FormDialog';

const companySchema = z.object({
  name: z.string().trim().min(1, 'Введите название'),
});

type CompanyValues = z.infer<typeof companySchema>;

interface CompanyFormDialogProps {
  /** Изменяемая компания; без неё форма создаёт новую. */
  company?: Company;
  onClose: () => void;
}

export function CompanyFormDialog({ company, onClose }: CompanyFormDialogProps) {
  const save = useResourceMutation(
    (values: CompanyValues) =>
      company ? companies.update(company.uuid, values) : companies.create(values),
    company ? 'Компания изменена' : 'Компания создана',
  );
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CompanyValues>({
    resolver: zodResolver(companySchema),
    defaultValues: { name: company?.name ?? '' },
  });

  return (
    <FormDialog
      title={company ? 'Изменить компанию' : 'Новая компания'}
      error={save.error}
      pending={save.isPending}
      onSubmit={handleSubmit((values) => save.mutate(values, { onSuccess: onClose }))}
      onClose={onClose}
    >
      <TextField label="Название" autoFocus {...errorProps(errors.name)} {...register('name')} />
    </FormDialog>
  );
}
