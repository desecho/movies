import axios from "axios";
import { ref, type Ref } from "vue";

import type { RecordType, SortData } from "../types";

import { listWatchedId } from "../const";
import { getUrl } from "../helpers";
import { $toast } from "../toast";

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

    /**
     * Add movie to a list
     */
    function addToList(
        movieId: number,
        listId: number,
        record?: RecordType,
    ): void {
        axios
            .post(getUrl(`add-to-list/${movieId}/`), { listId })
            .then(() => {
                if (record !== undefined) {
                    record.listId = listId;
                    record.additionDate = Date.now();
                }
            })
            .catch(() => {
                $toast.error("Error adding the movie to the list");
            });
    }

    /**
     * Add movie to user's own list (when viewing profile)
     */
    function addToMyList(
        movieId: number,
        listId: number,
        records: RecordType[],
        myRecords: RecordType[],
        isLoggedIn: boolean,
    ): void {
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
            addToList(movieId, listId); // Call the existing addToList function

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
    function removeRecord(record: RecordType, records: RecordType[]): void {
        // Optimistically remove from UI first
        const actualIndex = records.findIndex((r) => r.id === record.id);
        if (actualIndex !== -1) {
            records.splice(actualIndex, 1);
        }

        axios
            .delete(getUrl(`remove-record/${record.id}/`))
            .then(() => {
                // Record already removed optimistically
            })
            .catch(() => {
                // Restore the record if deletion fails
                if (actualIndex !== -1) {
                    records.splice(actualIndex, 0, record);
                }
                $toast.error("Error removing the movie");
            });
    }

    /**
     * Change movie rating
     */
    function changeRating(record: RecordType, rating: number): void {
        // Store the original rating before the change
        const originalRating = record.rating;

        // Optimistically update the rating
        record.rating = rating;

        axios
            .put(getUrl(`change-rating/${record.id}/`), { rating })
            .then(() => {
                // Update the original rating to the new confirmed value
                record.ratingOriginal = rating;
            })
            .catch(() => {
                // Revert to the original rating if the save fails
                record.rating = originalRating;
                $toast.error("Error saving the rating");
            });
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
        addToList,
        addToMyList,
        removeRecord,
        changeRating,
        saveOptions,
        saveComment,
        showCommentArea,
        updateRecordComment,
        saveRecordsOrder,
        moveToTop,
        moveToBottom,
    };
}
