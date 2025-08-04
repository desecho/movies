// Styles
// eslint-disable-next-line import/no-unassigned-import
import "@mdi/font/css/materialdesignicons.css";
// eslint-disable-next-line import/no-unassigned-import
import "vuetify/styles";

// Vuetify
import { createVuetify } from "vuetify";

// Native Vuetify themes with custom colors integrated
const lightTheme = {
    dark: false,
    colors: {
        primary: "#667eea",
        "primary-darken-1": "#5a67d8",
        secondary: "#764ba2",
        "secondary-darken-1": "#6b46c1",
        accent: "#f093fb",
        error: "#ef4444",
        warning: "#f59e0b",
        info: "#3b82f6",
        success: "#10b981",
        surface: "#ffffff",
        "surface-variant": "#f8f9fa",
        "on-surface": "#2d3748",
        "on-surface-variant": "#6c757d",
        background: "#ffffff",
        "on-background": "#2d3748",
    },
    variables: {
        "border-color": "#e2e8f0",
        "border-opacity": 0.12,
        "high-emphasis-opacity": 0.87,
        "medium-emphasis-opacity": 0.6,
        "disabled-opacity": 0.38,
        "idle-opacity": 0.04,
        "hover-opacity": 0.04,
        "focus-opacity": 0.12,
        "selected-opacity": 0.08,
        "activated-opacity": 0.12,
        "pressed-opacity": 0.12,
        "dragged-opacity": 0.08,
        "theme-kbd": "#212529",
        "theme-on-kbd": "#ffffff",
        "theme-code": "#f5f5f5",
        "theme-on-code": "#000000",
    },
};

const darkTheme = {
    dark: true,
    colors: {
        primary: "#667eea",
        "primary-darken-1": "#5a67d8",
        secondary: "#764ba2",
        "secondary-darken-1": "#6b46c1",
        accent: "#f093fb",
        error: "#ef4444",
        warning: "#f59e0b",
        info: "#3b82f6",
        success: "#10b981",
        surface: "#334155",
        "surface-variant": "#475569",
        "on-surface": "#f1f5f9",
        "on-surface-variant": "#94a3b8",
        background: "#1e293b",
        "on-background": "#f1f5f9",
    },
    variables: {
        "border-color": "#475569",
        "border-opacity": 0.12,
        "high-emphasis-opacity": 0.87,
        "medium-emphasis-opacity": 0.6,
        "disabled-opacity": 0.38,
        "idle-opacity": 0.04,
        "hover-opacity": 0.04,
        "focus-opacity": 0.12,
        "selected-opacity": 0.08,
        "activated-opacity": 0.12,
        "pressed-opacity": 0.12,
        "dragged-opacity": 0.08,
        "theme-kbd": "#212529",
        "theme-on-kbd": "#ffffff",
        "theme-code": "#1e1e1e",
        "theme-on-code": "#cccccc",
    },
};

export default createVuetify({
    theme: {
        defaultTheme: "light",
        themes: {
            light: lightTheme,
            dark: darkTheme,
        },
        variations: {
            colors: ["primary", "secondary", "accent"],
            lighten: 4,
            darken: 4,
        },
    },
    defaults: {
        VBtn: {
            style: [{ textTransform: "none" }, { fontWeight: "500" }],
        },
        VCard: {
            elevation: 2,
        },
        VTextField: {
            variant: "outlined",
        },
        VSelect: {
            variant: "outlined",
        },
    },
});
