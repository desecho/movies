import axios from "axios";

import type { AxiosError, AxiosRequestHeaders } from "axios";

import { router } from "./router";
import { useAuthStore } from "./stores/auth";

export function initAxios(): void {
    const headers: AxiosRequestHeaders = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    };

    const { user, refreshToken } = useAuthStore();
    if (user.isLoggedIn) {
        // Use `!` because we know that access token is not null when user is logged in
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        headers.Authorization = `Bearer ${user.accessToken!}`;
    }

    axios.defaults.headers.common = headers;
    axios.interceptors.response.use(
        (response) => {
            return response;
        },
        async (error: AxiosError) => {
            if (error.response?.status === 401) {
                if (user.isLoggedIn) {
                    // Check if the error response contains token_not_valid in the data
                    const errorData = error.response.data as {
                        code?: string;
                        detail?: string;
                    };
                    if (
                        errorData?.code === "token_not_valid" ||
                        errorData?.detail ===
                            "Given token not valid for any token type"
                    ) {
                        try {
                            await refreshToken();
                            // Retry the original request with the new token
                            if (error.config) {
                                return axios.request(error.config);
                            }
                        } catch (err) {
                            // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
                            return Promise.reject(err);
                        }
                    }
                    return Promise.reject(error);
                }
                void router.push("/login");
            }
            return Promise.reject(error);
        },
    );
}
