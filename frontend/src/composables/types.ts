/* Copied from vuetify. It looks like these are local types. */
interface FieldValidationResult {
    id: number | string;
    errorMessages: string[];
}

export interface FormValidationResult {
    valid: boolean;
    errors: FieldValidationResult[];
}

/* --------------------------------------------------------- */
export interface Form {
    validate: () => Promise<FormValidationResult>;
}
