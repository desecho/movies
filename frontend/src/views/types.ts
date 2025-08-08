export interface GetUserPreferencesData {
    hidden: boolean;
    country?: string;
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

export interface AvatarUploadResponse {
    avatar_url: string;
}

export interface AvatarUploadError {
    avatar?: string[];
    detail?: string;
}
