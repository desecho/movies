import axios from "axios";
import { defineStore } from "pinia";
import { ref } from "vue";

import type { Ref } from "vue";

import { getUrl } from "../helpers";

interface FeedUser {
    username: string;
    avatarUrl: string | null;
}

interface FeedMovie {
    id: number;
    title: string;
    posterSmall: string | null;
    releaseDate: string | null;
    tmdbId: number;
}

interface FeedAction {
    id: number;
    name: string;
}

interface FeedList {
    id: number;
    name: string;
}

interface FeedItem {
    id: number;
    user: FeedUser;
    action: FeedAction;
    movie: FeedMovie;
    date: string;
    list?: FeedList;
    rating?: number;
    comment?: string;
}

interface FeedResponse {
    results: FeedItem[];
    next: string | null;
    previous: string | null;
    count: number;
}

interface FollowStatus {
    isFollowing: boolean;
    followersCount: number;
    followingCount: number;
}

export const useFeedStore = defineStore("feed", () => {
    // Feed state
    const feedItems: Ref<FeedItem[]> = ref([]);
    const feedLoading = ref(false);
    const feedError: Ref<string | null> = ref(null);
    const hasMore = ref(false);
    const nextPage: Ref<string | null> = ref(null);

    // Follow state
    const followCache: Ref<Record<string, FollowStatus>> = ref({});

    // Feed actions
    async function loadFeed(reset = true): Promise<void> {
        feedLoading.value = true;
        feedError.value = null;

        try {
            const url = reset
                ? getUrl("feed/")
                : nextPage.value || getUrl("feed/");
            const response = await axios.get(url);
            const data = response.data as FeedResponse;

            if (reset) {
                feedItems.value = data.results;
            } else {
                feedItems.value.push(...data.results);
            }

            hasMore.value = Boolean(data.next);
            // eslint-disable-next-line require-atomic-updates
            nextPage.value = data.next;
        } catch (error) {
            console.error("Error loading feed:", error);
            feedError.value = "Failed to load activity feed";
            throw error;
        } finally {
            feedLoading.value = false;
        }
    }

    async function loadMore(): Promise<void> {
        if (!hasMore.value || feedLoading.value) {
            return;
        }

        await loadFeed(false);
    }

    function clearFeed(): void {
        feedItems.value = [];
        hasMore.value = false;
        nextPage.value = null;
        feedError.value = null;
    }

    // Follow actions
    async function getFollowStatus(username: string): Promise<FollowStatus> {
        // Check cache first
        if (followCache.value[username]) {
            return followCache.value[username];
        }

        try {
            const response = await axios.get(getUrl(`follow/${username}/`));
            const apiResponse = response.data as {
                is_following: boolean;
                followers_count: number;
                following_count: number;
            };

            const status: FollowStatus = {
                isFollowing: apiResponse.is_following,
                followersCount: apiResponse.followers_count,
                followingCount: apiResponse.following_count,
            };

            // Cache the result
            followCache.value = { ...followCache.value, [username]: status };
            return status;
        } catch (error) {
            console.error("Error loading follow status:", error);
            // Return default status on error
            const defaultStatus: FollowStatus = {
                isFollowing: false,
                followersCount: 0,
                followingCount: 0,
            };
            followCache.value[username] = defaultStatus;
            return defaultStatus;
        }
    }

    async function followUser(username: string): Promise<FollowStatus> {
        try {
            const response = await axios.post(getUrl(`follow/${username}/`));
            const apiResponse = response.data as {
                is_following: boolean;
                followers_count: number;
                following_count: number;
            };

            const status: FollowStatus = {
                isFollowing: apiResponse.is_following,
                followersCount: apiResponse.followers_count,
                followingCount: apiResponse.following_count,
            };

            // Update cache
            followCache.value[username] = status;
            return status;
        } catch (error) {
            console.error("Error following user:", error);
            throw error;
        }
    }

    async function unfollowUser(username: string): Promise<FollowStatus> {
        try {
            const response = await axios.delete(getUrl(`follow/${username}/`));
            const apiResponse = response.data as {
                is_following: boolean;
                followers_count: number;
                following_count: number;
            };

            const status: FollowStatus = {
                isFollowing: apiResponse.is_following,
                followersCount: apiResponse.followers_count,
                followingCount: apiResponse.following_count,
            };

            // Update cache
            followCache.value[username] = status;
            return status;
        } catch (error) {
            console.error("Error unfollowing user:", error);
            throw error;
        }
    }

    async function toggleFollow(username: string): Promise<FollowStatus> {
        const currentStatus = await getFollowStatus(username);

        if (currentStatus.isFollowing) {
            return unfollowUser(username);
        }
        return followUser(username);
    }

    function clearFollowCache(): void {
        followCache.value = {};
    }

    function updateFollowStatusInCache(
        username: string,
        status: FollowStatus,
    ): void {
        followCache.value[username] = status;
    }

    return {
        // Feed state
        feedItems,
        feedLoading,
        feedError,
        hasMore,
        nextPage,

        // Follow state
        followCache,

        // Feed actions
        loadFeed,
        loadMore,
        clearFeed,

        // Follow actions
        getFollowStatus,
        followUser,
        unfollowUser,
        toggleFollow,
        clearFollowCache,
        updateFollowStatusInCache,
    };
});

export type {
    FeedItem,
    FeedUser,
    FeedMovie,
    FeedAction,
    FeedList,
    FollowStatus,
};
