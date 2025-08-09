import axios from "axios";
import { ref, type Ref } from "vue";

import type { RecordType, SortData } from "../types";

import { listWatchedId } from "../const";
import { getUrl } from "../helpers";
import { $toast } from "../toast";

import { useApiCall } from "./useAsyncOperation";

export function useMovieOperations(): {
    addingToList: Ref<Record<string, boolean>>;
    addToList: (movieId: number, listId: number, record?: RecordType) => void;
    addToMyList: (
        movieId: number,
        listId: number,
        records: RecordType[],
        myRecords: RecordType[],
        isLoggedIn: boolean,
    ) => void;
    removeRecord: (record: RecordType, records: RecordType[]) => void;
    changeRating: (record: RecordType, rating: number) => void;
    saveOptions: (
        record: RecordType,
        field: keyof RecordType["options"],
    ) => void;
    saveComment: (record: RecordType) => void;
    showCommentArea: (record: RecordType) => void;
    updateRecordComment: (record: RecordType, comment: string) => void;
    saveRecordsOrder: (records: RecordType[]) => void;
    moveToTop: (record: RecordType, records: RecordType[]) => void;
    moveToBottom: (record: RecordType, records: RecordType[]) => void;
} {
    // Track loading state for add to list buttons
    const addingToList = ref<Record<string, boolean>>({});

    // Error handling composables
    const addToListOperation = useApiCall("Add Movie to List");
    const removeRecordOperation = useApiCall("Remove Movie from List");
    const updateRecordOperation = useApiCall("Update Movie Record");

    /**
     * Add movie to a list
     */
    async function addToList(
        movieId: number,
        listId: number,
        record?: RecordType,
    ): Promise<void> {
        const result = await addToListOperation.execute(async () => {
            const response = await axios.post(
                getUrl(`add-to-list/${movieId}/`),
                { listId },
            );
            return response.data as Record<string, unknown>;
        });

        if (result.success) {
            if (record !== undefined) {
                record.listId = listId;
                record.additionDate = Date.now();
            }
            $toast.success("Movie added to your list!");
        }
    }

    /**
     * Add movie to user's own list (when viewing profile)
     */
    async function addToMyList(
        movieId: number,
        listId: number,
        records: RecordType[],
        myRecords: RecordType[],
        isLoggedIn: boolean,
    ): Promise<void> {
        if (!isLoggedIn) {
            $toast.error("You must be logged in to add movies to your list");
            return;
        }

        const loadingKey = `${movieId}-${listId}`;
        addingToList.value[loadingKey] = true;

        try {
            // Add to myRecords for immediate UI update
            const movieData = records.find(
                (record) => record.movie.id === movieId,
            )?.movie;
            await addToList(movieId, listId); // Call the existing addToList function

            if (movieData) {
                const newRecord: RecordType = {
                    id: Date.now(),
                    movie: movieData,
                    listId,
                    rating: 0,
                    comment: "",
                    additionDate: Date.now(),
                    order: myRecords.length + 1,
                    options: {
                        original: false,
                        extended: false,
                        theatre: false,
                        hd: false,
                        fullHd: false,
                        ultraHd: false,
                        ignoreRewatch: false,
                    },
                    providerRecords: [],
                    ratingOriginal: 0,
                    commentArea: false,
                };
                myRecords.push(newRecord);
            }

            const listName = listId === listWatchedId ? "Watched" : "To Watch";
            $toast.success(`Movie added to your ${listName} list`);
        } catch (error) {
            console.log("Error adding movie to list:", error);
            $toast.error("Error adding movie to your list");
        } finally {
            addingToList.value[loadingKey] = false;
        }
    }

    /**
     * Remove record from list
     */
    async function removeRecord(
        record: RecordType,
        records: RecordType[],
    ): Promise<void> {
        // Optimistically remove from UI first
        const actualIndex = records.findIndex((r) => r.id === record.id);
        if (actualIndex !== -1) {
            records.splice(actualIndex, 1);
        }

        const result = await removeRecordOperation.execute(async () => {
            const response = await axios.delete(
                getUrl(`remove-record/${record.id}/`),
            );
            return response.data as Record<string, unknown>;
        });

        if (result.success) {
            $toast.success("Movie removed from your list!");
        } else if (actualIndex !== -1) {
            // Restore the record if deletion fails
            records.splice(actualIndex, 0, record);
        }
    }

    /**
     * Change movie rating
     */
    async function changeRating(
        record: RecordType,
        rating: number,
    ): Promise<void> {
        // Store the original rating before the change
        const originalRating = record.rating;

        // Optimistically update the rating
        record.rating = rating;

        const result = await updateRecordOperation.execute(async () => {
            const response = await axios.put(
                getUrl(`change-rating/${record.id}/`),
                { rating },
            );
            return response.data as Record<string, unknown>;
        });

        if (result.success) {
            // Update the original rating to the new confirmed value
            // eslint-disable-next-line require-atomic-updates
            record.ratingOriginal = rating;
            $toast.success(`Rating updated to ${rating} stars!`);
        } else {
            // Revert to the original rating if the save fails
            // eslint-disable-next-line require-atomic-updates
            record.rating = originalRating;
        }
    }

    /**
     * Save record options
     */
    function saveOptions(
        record: RecordType,
        field: keyof RecordType["options"],
    ): void {
        // Store the original value for error rollback
        const originalValue = record.options[field];

        const data = {
            options: record.options,
        };

        axios.put(getUrl(`record/${record.id}/options/`), data).catch(() => {
            // Revert to the original value if save fails
            record.options[field] = originalValue;
            $toast.error("Error saving options");
        });
    }

    /**
     * Save comment
     */
    function saveComment(record: RecordType): void {
        const data = {
            comment: record.comment,
        };

        axios
            .put(getUrl(`save-comment/${record.id}/`), data)
            .then(() => {
                if (record.comment === "") {
                    record.commentArea = false;
                }
            })
            .catch(() => {
                $toast.error("Error saving a comment");
            });
    }

    /**
     * Show comment area
     */
    function showCommentArea(record: RecordType): void {
        record.commentArea = true;
    }

    /**
     * Update record comment from child component
     */
    function updateRecordComment(record: RecordType, comment: string): void {
        record.comment = comment;
    }

    /**
     * Save records order
     */
    function saveRecordsOrder(records: RecordType[]): void {
        function getSortData(): SortData[] {
            const data: SortData[] = [];
            records.forEach((record) => {
                // Use the record's already-set order value, not the array index
                const sortData = { id: record.id, order: record.order };
                data.push(sortData);
            });
            return data;
        }

        const sortData = getSortData();

        axios
            .put(getUrl("save-records-order/"), { records: sortData })
            .then(() => {
                // Order saved successfully
            })
            .catch((error) => {
                console.error("Error saving movie order:", error);
                $toast.error("Error saving movie order");
            });
    }

    /**
     * Move record to top
     */
    function moveToTop(record: RecordType, records: RecordType[]): void {
        const actualIndex = records.findIndex((r) => r.id === record.id);
        if (actualIndex !== -1) {
            records.splice(actualIndex, 1);
            records.unshift(record);
            saveRecordsOrder(records);
        }
    }

    /**
     * Move record to bottom
     */
    function moveToBottom(record: RecordType, records: RecordType[]): void {
        const actualIndex = records.findIndex((r) => r.id === record.id);
        if (actualIndex !== -1) {
            records.splice(actualIndex, 1);
            records.push(record);
            saveRecordsOrder(records);
        }
    }

    return {
        // State
        addingToList,

        // Methods
        addToList: (
            movieId: number,
            listId: number,
            record?: RecordType,
        ): void => {
            void addToList(movieId, listId, record);
        },
        addToMyList: (
            movieId: number,
            listId: number,
            records: RecordType[],
            myRecords: RecordType[],
            isLoggedIn: boolean,
        ): void => {
            void addToMyList(movieId, listId, records, myRecords, isLoggedIn);
        },
        removeRecord: (record: RecordType, records: RecordType[]): void => {
            void removeRecord(record, records);
        },
        changeRating: (record: RecordType, rating: number): void => {
            void changeRating(record, rating);
        },
        saveOptions,
        saveComment,
        showCommentArea,
        updateRecordComment,
        saveRecordsOrder,
        moveToTop,
        moveToBottom,
    };
}
