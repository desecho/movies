export interface UserStore {
    isLoggedIn: boolean;
    refreshToken?: string;
    accessToken?: string;
    username?: string;
}

export interface TokenData {
    refresh: string;
    access: string;
}

export interface TokenRefreshData {
    access: string;
}
