import { defineStore } from "pinia";
import { ref, watch } from "vue";
import { useTheme } from "vuetify";

export const useThemeStore = defineStore(
    "theme",
    () => {
        const isDark = ref(false);
        let vuetifyTheme: ReturnType<typeof useTheme> | null = null;

        // Initialize Vuetify theme after app is mounted
        function initVuetifyTheme(): void {
            try {
                vuetifyTheme = useTheme();
            } catch {
                // Vuetify theme not available yet, will retry later
            }
        }

        // Apply theme to both document and Vuetify
        function applyTheme(): void {
            // Apply CSS class-based theme (for custom styles)
            if (isDark.value) {
                document.documentElement.classList.add("dark-theme");
                document.documentElement.classList.remove("light-theme");
            } else {
                document.documentElement.classList.add("light-theme");
                document.documentElement.classList.remove("dark-theme");
            }

            // Apply Vuetify native theme
            if (vuetifyTheme) {
                vuetifyTheme.global.name.value = isDark.value
                    ? "dark"
                    : "light";
            }
        }

        // Initialize theme on startup
        function initTheme(): void {
            /* For first-time users (no persisted state), set system preference.
           The plugin will handle persistence automatically from this point on. */
            const hasPersistedState = localStorage.getItem("theme") !== null;
            if (!hasPersistedState) {
                isDark.value = window.matchMedia(
                    "(prefers-color-scheme: dark)",
                ).matches;
            }

            // Initialize Vuetify theme if not already done
            if (!vuetifyTheme) {
                initVuetifyTheme();
            }

            applyTheme();
        }

        // Toggle theme
        function toggleTheme(): void {
            isDark.value = !isDark.value;
        }

        // Watch for theme changes and apply them
        watch(isDark, () => {
            applyTheme();
        });

        // Listen for system theme changes
        const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
        mediaQuery.addEventListener("change", (e) => {
            // Only update if no user preference has been persisted yet (first-time user)
            const hasPersistedState = localStorage.getItem("theme") !== null;
            if (!hasPersistedState) {
                isDark.value = e.matches;
            }
        });

        return {
            isDark,
            initTheme,
            toggleTheme,
            applyTheme,
            initVuetifyTheme,
        };
    },
    {
        persist: {
            key: "theme",
        },
    },
);
