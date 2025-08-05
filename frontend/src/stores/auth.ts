import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { defineStore } from "pinia";

import type { JWTDecoded } from "../types";
import type { TokenData, TokenRefreshData, UserStore } from "./types";
import type { AvatarUploadResponse } from "../views/types";

import { initAxios } from "../axios";
import { getUrl } from "../helpers";
import { router } from "../router";

const userDefault: UserStore = {
    isLoggedIn: false,
};

export const useAuthStore = defineStore("auth", {
    state: () => ({
        user: userDefault,
    }),
    persist: {
        enabled: true,
        strategies: [
            {
                key: "user",
                storage: localStorage,
            },
        ],
    },
    actions: {
        async login(username: string, password: string) {
            const response = await axios.post(getUrl("token/"), {
                username,
                password,
            });
            const data = response.data as TokenData;
            this.user = {
                refreshToken: data.refresh,
                accessToken: data.access,
                isLoggedIn: true,
                username,
            };
            initAxios();

            // Load user's avatar after successful login
            await this.loadAvatar();

            void router.push("/");
        },
        // This function needs to be called only when user is logged in
        async refreshToken() {
            // Use `!` because we know that refresh token is not null when user is logged in
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            const decodedToken: JWTDecoded = jwtDecode(this.user.refreshToken!);
            // If refresh token expired we log the user out
            if (decodedToken.exp < Date.now() / 1000) {
                this.logout();
                return;
            }

            const response = await axios.post(getUrl("token/refresh/"), {
                refresh: this.user.refreshToken,
            });
            const data = response.data as TokenRefreshData;
            this.user.accessToken = data.access;
            initAxios();
        },
        async uploadAvatar(file: File) {
            const formData = new FormData();
            formData.append("avatar", file);

            const response = await axios.post(
                getUrl("user/avatar/"),
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                },
            );

            // Update user store with new avatar URL
            const data = response.data as AvatarUploadResponse;
            if (data.avatar_url) {
                this.user.avatarUrl = data.avatar_url;
            }
        },
        async deleteAvatar() {
            await axios.delete(getUrl("user/avatar/"));

            // Remove avatar URL from user store
            this.user.avatarUrl = undefined;
        },
        async loadAvatar() {
            try {
                const response = await axios.get(getUrl("user/avatar/"));
                const data = response.data as AvatarUploadResponse;
                if (data.avatar_url) {
                    this.user.avatarUrl = data.avatar_url;
                } else {
                    this.user.avatarUrl = undefined;
                }
            } catch {
                // If avatar loading fails, just set to undefined
                this.user.avatarUrl = undefined;
            }
        },
        logout() {
            this.user = userDefault;
            localStorage.removeItem("user");
            initAxios();
            void router.push("/");
        },
    },
});
