import { router } from "./router";
import { useAuthStore } from "./stores/auth";

export const rulesHelper = {
    required: (value: string): "Required" | true =>
        Boolean(value) || "Required",
};

export function getUrl(path: string): string {
    const baseUrl = import.meta.env.VITE_BACKEND_URL as string;
    return `${baseUrl}${path}`;
}

export function requireAuthenticated(): void {
    const { user } = useAuthStore();
    if (!user.isLoggedIn) {
        void router.push("/login");
    }
}

export function getSrcSet(img1x: string, img2x: string): string {
    return `${img1x} 1x, ${img2x} 2x`;
}
