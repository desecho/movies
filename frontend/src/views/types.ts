export interface GetUserPreferencesData {
    hidden: boolean;
}

export interface TokenErrorData {
    detail: string;
}

export interface RegistrationErrorData {
    detail: string;
}

export interface CheckEmailAvailabilityErrorData {
    password?: string[];
    email?: string[];
    username?: string[];
}

export interface ChangePasswordErrorData {
    old_password?: string[];
    password?: string[];
}
