import type { FieldError } from 'react-hook-form';

/** Свойства поля MUI для показа ошибки валидации. */
export function errorProps(error?: FieldError): { error: boolean; helperText?: string } {
  return { error: Boolean(error), helperText: error?.message };
}
