import axios from "axios";

import type { AxiosError, AxiosRequestHeaders } from "axios";

import { router } from "./router";
import { useAuthStore } from "./stores/auth";
import { isValidToken } from "./types/common";

// Keep track of the active response interceptor so we can eject it
let responseInterceptorId: number | null = null;

export function initAxios(): void {
    const headers: AxiosRequestHeaders = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    };

    const auth = useAuthStore();
    if (auth.user.isLoggedIn && isValidToken(auth.user.accessToken)) {
        headers.Authorization = `Bearer ${auth.user.accessToken}`;
    }

    axios.defaults.headers.common = headers;

    // Eject previously registered interceptor to avoid leaks and stale closures
    if (responseInterceptorId !== null) {
        axios.interceptors.response.eject(responseInterceptorId);
        responseInterceptorId = null;
    }

    responseInterceptorId = axios.interceptors.response.use(
        (response) => {
            return response;
        },
        async (error: AxiosError) => {
            if (error.response?.status === 401) {
                const currentAuth = useAuthStore();
                if (currentAuth.user.isLoggedIn) {
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
                            await currentAuth.refreshToken();
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
