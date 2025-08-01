import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { defineStore } from "pinia";

import type { JWTDecoded } from "../types";
import type { TokenData, TokenRefreshData, UserStore } from "./types";

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
        logout() {
            this.user = userDefault;
            localStorage.removeItem("user");
            initAxios();
            void router.push("/");
        },
    },
});
