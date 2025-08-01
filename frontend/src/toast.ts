import { useToast } from "vue-toast-notification";
// eslint-disable-next-line import/no-unassigned-import
import "vue-toast-notification/dist/theme-default.css";

export const $toast = useToast({
    position: "bottom-right",
    duration: 1500,
});
