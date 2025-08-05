import axios from "axios";
import { defineStore } from "pinia";

import type { RecordType } from "../types";

import { getUrl } from "../helpers";
import { router } from "../router";

import { useAuthStore } from "./auth";

const recordsInitialState: RecordType[] = [];

function roundToHalfStar(rating: number): number {
    return Math.round(rating * 2) / 2;
}

export const useRecordsStore = defineStore("records", {
    state: () => ({
        records: recordsInitialState,
        areLoaded: false,
        isLoading: false,
        currentUsername: null as string | null,
    }),
    actions: {
        async loadRecords(username?: string, reload = false) {
            // If loading profile records, we don't need authentication
            if (!username) {
                const { user } = useAuthStore();
                if (!user.isLoggedIn) {
                    void router.push("/login");
                    return;
                }
            }

            // Force reload if switching between different contexts (profile vs personal, or different users)
            const contextChanged = this.currentUsername !== (username || null);
            const shouldReload = reload || contextChanged;

            // Check if we already have the right data loaded
            if (this.areLoaded && !shouldReload) {
                return;
            }

            // Set loading state
            this.isLoading = true;

            // Clear existing records when context changes
            if (contextChanged) {
                this.records = [];
                this.areLoaded = false;
            }

            try {
                let url: string;
                if (username) {
                    // Load records for a specific user's profile
                    url = getUrl(`users/${username}/records/`);
                    this.currentUsername = username;
                } else {
                    // Load records for the current logged-in user
                    url = getUrl("records/");
                    this.currentUsername = null;
                }

                const response = await axios.get(url);
                this.areLoaded = true;
                const recs: RecordType[] = response.data as RecordType[];
                recs.forEach((record) => {
                    record.ratingOriginal = record.rating;
                    // Convert IMDb rating to a 0-5 scale
                    const convertedRating = (record.movie.imdbRating / 10) * 5;
                    record.movie.imdbRatingConverted =
                        roundToHalfStar(convertedRating);
                });
                this.records = response.data as RecordType[];

                if (username) {
                    console.log(`Records loaded for user: ${username}`);
                } else {
                    console.log("Records loaded");
                }
            } finally {
                this.isLoading = false;
            }
        },
        async reloadRecords() {
            await this.loadRecords(this.currentUsername || undefined, true);
        },
    },
});
