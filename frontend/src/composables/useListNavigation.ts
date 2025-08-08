import { computed, type ComputedRef, ref, type Ref, watch } from "vue";
import { useRouter } from "vue-router";

import { listWatchedId } from "../const";

export function useListNavigation(
    initialListId: number,
    isProfileView: boolean = false,
): {
    selectedProfileList: Ref<number>;
    selectedUserList: Ref<number>;
    currentListId: ComputedRef<number>;
    page: Ref<number>;
    handleProfileListChange: (
        newListId: number,
        username: string,
        onDataReload: () => Promise<void>,
    ) => Promise<void>;
    handleUserListChange: (
        newListId: number,
        onDataReload: () => Promise<void>,
    ) => Promise<void>;
    initializeWatchers: (
        username: string | undefined,
        onDataReload: () => Promise<void>,
    ) => void;
    resetListSelections: (listId: number) => void;
} {
    const router = useRouter();

    // For profile views, allow switching between lists
    const selectedProfileList = ref(initialListId);

    // For regular users, allow switching between their own lists
    const selectedUserList = ref(initialListId);

    // Current page for pagination
    const page = ref(1);

    // Computed property to get the current list ID (either from props or selected by user)
    const currentListId = computed(() => {
        return isProfileView
            ? selectedProfileList.value
            : selectedUserList.value;
    });

    /**
     * Handle profile list selection changes
     */
    async function handleProfileListChange(
        newListId: number,
        username: string,
        onDataReload: () => Promise<void>,
    ): Promise<void> {
        if (!isProfileView || !username) {
            return;
        }

        page.value = 1; // Reset to first page when switching lists

        // Navigate to the appropriate profile route
        const newPath =
            newListId === listWatchedId
                ? `/users/${username}/list/watched`
                : `/users/${username}/list/to-watch`;

        if (router.currentRoute.value.path !== newPath) {
            await router.push(newPath);
        }

        // Re-load data to ensure we have the latest order values
        await onDataReload();
    }

    /**
     * Handle user list selection changes (for regular users)
     */
    async function handleUserListChange(
        newListId: number,
        onDataReload: () => Promise<void>,
    ): Promise<void> {
        if (isProfileView) {
            return;
        }

        page.value = 1; // Reset to first page when switching lists

        // Navigate to the appropriate route
        const newPath =
            newListId === listWatchedId ? "/list/watched" : "/list/to-watch";
        if (router.currentRoute.value.path !== newPath) {
            await router.push(newPath);
        }

        // Re-load data to ensure we have the latest order values
        await onDataReload();
    }

    /**
     * Initialize watchers for list changes
     */
    function initializeWatchers(
        username: string | undefined,
        onDataReload: () => Promise<void>,
    ): void {
        // Watch for profile list selection changes
        watch(selectedProfileList, async (newListId) => {
            if (username) {
                await handleProfileListChange(
                    newListId,
                    username,
                    onDataReload,
                );
            }
        });

        // Watch for user list selection changes (for regular users)
        watch(selectedUserList, async (newListId) => {
            await handleUserListChange(newListId, onDataReload);
        });
    }

    /**
     * Reset list selections to initial values
     */
    function resetListSelections(listId: number): void {
        selectedProfileList.value = listId;
        selectedUserList.value = listId;
    }

    return {
        // State
        selectedProfileList,
        selectedUserList,
        currentListId,
        page,

        // Methods
        handleProfileListChange,
        handleUserListChange,
        initializeWatchers,
        resetListSelections,
    };
}
