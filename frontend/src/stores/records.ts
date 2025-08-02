import axios from "axios";
import { defineStore } from "pinia";

import type { RecordType } from "../types";

import { getUrl } from "../helpers";
import { router } from "../router";

import { useAuthStore } from "./auth";

const recordsInitialState: RecordType[] = [];

export const useRecordsStore = defineStore("records", {
    state: () => ({
        records: recordsInitialState,
        areLoaded: false,
    }),
    actions: {
        async loadRecords(reload = false) {
            const { user } = useAuthStore();
            if (!user.isLoggedIn) {
                void router.push("/login");
            }
            if (this.areLoaded && !reload) {
                return;
            }

            const response = await axios.get(getUrl("records/"));
            this.areLoaded = true;
            const recs: RecordType[] = response.data as RecordType[];
            recs.forEach((record) => {
                record.ratingOriginal = record.rating;
            });
            this.records = response.data as RecordType[];
        },
        async reloadRecords() {
            await this.loadRecords(true);
        },
    },
});
