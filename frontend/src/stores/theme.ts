import { defineStore } from "pinia";
import { ref, watch } from "vue";

export const useThemeStore = defineStore("theme", () => {
    const isDark = ref(false);

    // Apply theme to document
    function applyTheme(): void {
        if (isDark.value) {
            document.documentElement.classList.add("dark-theme");
            document.documentElement.classList.remove("light-theme");
        } else {
            document.documentElement.classList.add("light-theme");
            document.documentElement.classList.remove("dark-theme");
        }
    }

    // Load theme preference from localStorage
    function initTheme(): void {
        const savedTheme = localStorage.getItem("theme");
        if (savedTheme) {
            isDark.value = savedTheme === "dark";
        } else {
            // Default to system preference
            isDark.value = window.matchMedia(
                "(prefers-color-scheme: dark)",
            ).matches;
        }
        applyTheme();
    }

    // Toggle theme
    function toggleTheme(): void {
        isDark.value = !isDark.value;
    }

    // Watch for theme changes and persist to localStorage
    watch(isDark, (newValue) => {
        localStorage.setItem("theme", newValue ? "dark" : "light");
        applyTheme();
    });

    // Listen for system theme changes
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    mediaQuery.addEventListener("change", (e) => {
        // Only update if no user preference is saved
        if (!localStorage.getItem("theme")) {
            isDark.value = e.matches;
        }
    });

    return {
        isDark,
        initTheme,
        toggleTheme,
        applyTheme,
    };
});
