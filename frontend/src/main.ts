// Styles
// eslint-disable-next-line import/no-unassigned-import
import "x-axios-progress-bar/dist/nprogress.css";
// eslint-disable-next-line import/no-unassigned-import
import "./styles/styles.scss";

import { createHead } from "@vueuse/head";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import { createApp } from "vue";
import { createGtag } from "vue-gtag";
import { loadProgressBar } from "x-axios-progress-bar";

import App from "./App.vue";
import { initAxios } from "./axios";
import vuetify from "./plugins/vuetify";
import { loadFonts } from "./plugins/webfontloader";
import { router } from "./router";

// eslint-disable-next-line @typescript-eslint/no-floating-promises, @typescript-eslint/explicit-function-return-type
(async () => {
    await loadFonts().catch(() => {
        throw new Error("Failed to load fonts");
    });
})();

loadProgressBar();

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const head = createHead();

const gtag = createGtag({
    tagId: import.meta.env.VITE_GOOGLE_ANALYTICS_ID as string,
    pageTracker: {
        router,
    },
});

createApp(App)
    .use(vuetify)
    .use(pinia)
    .use(router)
    .use(head)
    .use(gtag)
    .mount("#app");

/* Not entirely sure I need to init axios here.
   This has to be after creating an app because of pinia */
initAxios();
