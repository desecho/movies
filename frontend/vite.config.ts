/* eslint import/no-extraneous-dependencies: 0 */
/* eslint @typescript-eslint/strict-boolean-expressions: 0 */
/* eslint @typescript-eslint/no-unsafe-assignment: 0 */
/* eslint @typescript-eslint/no-unsafe-call: 0 */

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vite-plugin
import vuetify from "vite-plugin-vuetify";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue(), vuetify({ autoImport: true })],
    build: {
        target: "esnext",
    },
});
