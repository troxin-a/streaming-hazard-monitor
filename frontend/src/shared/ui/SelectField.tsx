import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';
import { type Control, type FieldPath, type FieldValues, useController } from 'react-hook-form';

import { errorProps } from './form';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps<T extends FieldValues> {
  control: Control<T>;
  name: FieldPath<T>;
  label: string;
  options: SelectOption[];
  onValueChange?: (value: string) => void;
}

/** Выпадающий список, связанный с полем формы. */
export function SelectField<T extends FieldValues>({
  control,
  name,
  label,
  options,
  onValueChange,
}: SelectFieldProps<T>) {
  const { field, fieldState } = useController({ control, name });

  return (
    <TextField
      select
      label={label}
      {...field}
      onChange={(event) => {
        field.onChange(event);
        onValueChange?.(event.target.value);
      }}
      {...errorProps(fieldState.error)}
    >
      {options.map((option) => (
        <MenuItem key={option.value} value={option.value}>
          {option.label}
        </MenuItem>
      ))}
    </TextField>
  );
}
