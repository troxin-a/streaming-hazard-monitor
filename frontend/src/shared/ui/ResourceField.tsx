import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import { useState } from 'react';
import { type Control, type FieldPath, type FieldValues, useController } from 'react-hook-form';

import { useResourceSearch } from '@/shared/api/hooks';
import type { Listable } from '@/shared/api/resource';
import { useDebouncedValue } from '@/shared/lib/useDebouncedValue';

import { errorProps } from './form';

interface Named {
  uuid: string;
  name: string;
}

interface ResourceFieldProps<T extends FieldValues, TOption extends Named> {
  control: Control<T>;
  /** Поле формы, в котором хранится uuid выбранной записи; пустая строка — ничего не выбрано. */
  name: FieldPath<T>;
  label: string;
  resource: Listable<TOption>;
  /** Запись, выбранная в форме при открытии. */
  initialOption?: TOption | null;
  /** Оставляет в списке только подходящие записи. */
  filter?: (option: TOption) => boolean;
  /** Подпись записи в списке; по умолчанию её название. */
  getLabel?: (option: TOption) => string;
  onValueChange?: (option: TOption | null) => void;
}

function getName(option: Named): string {
  return option.name;
}

/** Поле выбора записи с поиском по названию на сервере. */
export function ResourceField<T extends FieldValues, TOption extends Named>({
  control,
  name,
  label,
  resource,
  initialOption = null,
  filter,
  getLabel = getName,
  onValueChange,
}: ResourceFieldProps<T, TOption>) {
  const { field, fieldState } = useController({ control, name });
  const [selected, setSelected] = useState<TOption | null>(initialOption);
  const [search, setSearch] = useState('');
  const { data = [], isFetching } = useResourceSearch(resource, useDebouncedValue(search));

  const options = filter ? data.filter(filter) : data;
  // Форма может сбросить поле сама (например, здание при смене компании).
  const value = selected?.uuid === field.value ? selected : null;

  return (
    <Autocomplete
      options={options}
      value={value}
      loading={isFetching}
      getOptionLabel={getLabel}
      getOptionKey={(option) => option.uuid}
      isOptionEqualToValue={(option, current) => option.uuid === current.uuid}
      // Записи уже отобраны сервером по введённому тексту.
      filterOptions={(found) => found}
      onChange={(_, option) => {
        setSelected(option);
        field.onChange(option?.uuid ?? '');
        onValueChange?.(option);
      }}
      onInputChange={(_, text, reason) => setSearch(reason === 'input' ? text : '')}
      onBlur={field.onBlur}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder="Начните вводить название"
          inputRef={field.ref}
          {...errorProps(fieldState.error)}
        />
      )}
    />
  );
}
