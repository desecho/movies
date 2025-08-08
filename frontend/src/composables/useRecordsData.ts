import axios from "axios";
import { ref, type Ref } from "vue";

import type { RecordType } from "../types";

import { getUrl } from "../helpers";
import { useRecordsStore } from "../stores/records";
import { $toast } from "../toast";

import { useRequestDeduplication } from "./useRequestDeduplication";

export function useRecordsData() {
    const recordsStore = useRecordsStore();
    const { deduplicateRequest } = useRequestDeduplication();

    // User's own records for profile views
    const myRecords = ref<RecordType[]>([]);

    // User avatar for profile views
    const userAvatarUrl = ref<string | null>(null);

    /**
     * Load records data with deduplication
     */
    async function loadRecordsData(
        isProfileView?: boolean,
        username?: string,
    ): Promise<void> {
        const { loadRecords } = recordsStore;

        const cacheKey =
            isProfileView && username
                ? `records-profile-${username}`
                : "records-user";

        return deduplicateRequest(cacheKey, async () => {
            try {
                if (isProfileView && username) {
                    await loadRecords(username);
                } else {
                    await loadRecords();
                }
            } catch (error: unknown) {
                console.log(error);
                const errorMessage =
                    isProfileView && username
                        ? `Error loading ${username}'s movies`
                        : "Error loading movies";
                $toast.error(errorMessage);
                throw error; // Re-throw to prevent caching failed requests
            }
        });
    }

    /**
     * Load user's own records when viewing a profile (if logged in)
     */
    async function loadMyRecords(
        isProfileView?: boolean,
        isLoggedIn?: boolean,
    ): Promise<void> {
        if (isProfileView && isLoggedIn) {
            return deduplicateRequest("my-records", async () => {
                try {
                    const response = await axios.get(getUrl("records/"));
                    myRecords.value = response.data as RecordType[];
                } catch (error) {
                    console.log("Error loading user's records:", error);
                    throw error;
                }
            });
        }
    }

    /**
     * Load user avatar for profile views
     */
    async function loadUserAvatar(
        isProfileView?: boolean,
        username?: string,
    ): Promise<void> {
        if (isProfileView && username) {
            const cacheKey = `avatar-${username}`;
            return deduplicateRequest(cacheKey, async () => {
                try {
                    const response = await axios.get(
                        getUrl(`users/${username}/avatar/`),
                    );
                    const userData = response.data as {
                        username: string;
                        avatar_url: string | null;
                    };
                    userAvatarUrl.value = userData.avatar_url;
                } catch (error) {
                    console.log("Error loading user avatar:", error);
                    userAvatarUrl.value = null;
                    throw error;
                }
            });
        }
    }

    /**
     * Load all data in parallel
     */
    async function loadAllData(
        isProfileView?: boolean,
        username?: string,
        isLoggedIn?: boolean,
    ): Promise<void> {
        await Promise.all([
            loadRecordsData(isProfileView, username),
            loadMyRecords(isProfileView, isLoggedIn),
            loadUserAvatar(isProfileView, username),
        ]);
    }

    /**
     * Clear user-specific data
     */
    function clearUserData(): void {
        myRecords.value = [];
        userAvatarUrl.value = null;
    }

    return {
        // State
        myRecords,
        userAvatarUrl,

        // Methods
        loadRecordsData,
        loadMyRecords,
        loadUserAvatar,
        loadAllData,
        clearUserData,
    };
}
