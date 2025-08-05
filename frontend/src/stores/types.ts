export interface UserStore {
    isLoggedIn: boolean;
    refreshToken?: string;
    accessToken?: string;
    username?: string;
    avatarUrl?: string;
}

export interface TokenData {
    refresh: string;
    access: string;
}

export interface TokenRefreshData {
    access: string;
}
