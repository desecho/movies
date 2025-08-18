import { jwtDecode } from "jwt-decode";
import { createRouter, createWebHistory } from "vue-router";

import type { AuthProps, JWTDecoded } from "./types";
import type { RouteLocationNormalized } from "vue-router";

import { listToWatchId, listWatchedId } from "./const";
import { useAuthStore } from "./stores/auth";
import {
    getQueryParamAsNumber,
    getQueryParamAsString,
    isValidToken,
} from "./types/common";
import AboutView from "./views/AboutView.vue";
import ChangePasswordView from "./views/ChangePasswordView.vue";
import FeedView from "./views/FeedView.vue";
import FollowersView from "./views/FollowersView.vue";
import FollowingView from "./views/FollowingView.vue";
import LandingView from "./views/LandingView.vue";
import ListView from "./views/ListView.vue";
import LoginView from "./views/LoginView.vue";
import LogoutView from "./views/LogoutView.vue";
import MovieDetailView from "./views/MovieDetailView.vue";
import NetworkView from "./views/NetworkView.vue";
import RecommendationsView from "./views/RecommendationsView.vue";
import RegisterSuccessView from "./views/RegisterSuccessView.vue";
import RegistrationView from "./views/RegistrationView.vue";
import ResetPasswordRequestView from "./views/ResetPasswordRequestView.vue";
import ResetPasswordView from "./views/ResetPasswordView.vue";
import SearchView from "./views/SearchView.vue";
import StatsView from "./views/StatsView.vue";
import TrendingView from "./views/TrendingView.vue";
import UserPreferencesView from "./views/UserPreferencesView.vue";
import UsersView from "./views/UsersView.vue";
import VerifyUserView from "./views/VerifyUserView.vue";

function authProps(route: RouteLocationNormalized): AuthProps {
    return {
        userId: getQueryParamAsNumber(route.query.user_id, 0),
        timestamp: getQueryParamAsNumber(route.query.timestamp, 0),
        signature: getQueryParamAsString(route.query.signature, ""),
    };
}

export const router = createRouter({
    history: createWebHistory(),
    linkActiveClass: "active",
    routes: [
        // Landing page as home
        { path: "/", component: LandingView },

        { path: "/search", component: SearchView },
        { path: "/movie/:tmdbId", component: MovieDetailView, props: true },
        { path: "/about", component: AboutView },
        { path: "/preferences", component: UserPreferencesView },
        { path: "/stats", component: StatsView },
        { path: "/network", component: NetworkView },
        { path: "/feed", component: FeedView },
        { path: "/trending", component: TrendingView },
        { path: "/recommendations", component: RecommendationsView },
        {
            path: "/list/watched",
            component: ListView,
            props: { listId: listWatchedId },
        },
        {
            path: "/list/to-watch",
            component: ListView,
            props: { listId: listToWatchId },
        },
        { path: "/users", component: UsersView },
        { path: "/following", component: FollowingView },
        { path: "/followers", component: FollowersView },
        {
            path: "/users/:username/following",
            component: FollowingView,
            props: (route): Record<string, unknown> => ({
                username: route.params.username as string,
                isPublicView: true,
            }),
        },
        {
            path: "/users/:username/followers",
            component: FollowersView,
            props: (route): Record<string, unknown> => ({
                username: route.params.username as string,
                isPublicView: true,
            }),
        },
        {
            path: "/users/:username/list/watched",
            component: ListView,
            props: (route): Record<string, unknown> => ({
                username: route.params.username as string,
                listId: listWatchedId,
                isProfileView: true,
            }),
        },
        {
            path: "/users/:username/list/to-watch",
            component: ListView,
            props: (route): Record<string, unknown> => ({
                username: route.params.username as string,
                listId: listToWatchId,
                isProfileView: true,
            }),
        },
        { path: "/login", component: LoginView },
        { path: "/logout", component: LogoutView },
        { path: "/register", component: RegistrationView },
        {
            path: "/register/success",
            alias: "/register/success/",
            component: RegisterSuccessView,
        },
        {
            path: "/verify-user",
            component: VerifyUserView,
            props: authProps,
        },
        {
            path: "/reset-password",
            component: ResetPasswordView,
            props: authProps,
        },
        {
            path: "/reset-password-request",
            component: ResetPasswordRequestView,
        },
        { path: "/change-password", component: ChangePasswordView },
    ],
});

router.beforeEach(async (to) => {
    const privatePages = [
        "/preferences",
        "/change-password",
        "/stats",
        "/network",
    ];
    const authRequired = privatePages.includes(to.path);
    const { user, refreshToken } = useAuthStore();

    if (authRequired && !user.isLoggedIn) {
        return "/login";
    }

    if (user.isLoggedIn && isValidToken(user.accessToken)) {
        const decodedToken: JWTDecoded = jwtDecode(user.accessToken);
        // If token expired or is about to expire (in 30 minutes) we refresh it
        if (decodedToken.exp - Date.now() / 1000 < 30 * 60) {
            await refreshToken();
        }
    } else if (user.isLoggedIn && !isValidToken(user.accessToken)) {
        // If user is marked as logged in but has invalid token, redirect to login
        return "/login";
    }
});
