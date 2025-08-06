import { computed } from "vue";
import { useDisplay } from "vuetify";

import type { ComputedRef } from "vue";

export function useMobile(): {
    isPhone: ComputedRef<boolean>;
    isTablet: ComputedRef<boolean>;
    isMobile: ComputedRef<boolean>;
} {
    const { xs, sm, md, width } = useDisplay();

    /* Vuetify breakpoints:
       xs: 0-599px (phones)
       sm: 600-959px (tablets)
       md: 960-1279px (small desktop)
       iPad dimensions: 768px (standard), 834px (Pro), 1024px (Pro 12.9") */

    const isPhone = computed((): boolean => xs.value);
    const isTablet = computed((): boolean => {
        // Detect tablets by screen width (600px-1279px) and touch capability
        return (sm.value || (md.value && width.value < 1280)) && !xs.value;
    });

    /* Only treat actual phones (< 600px) as "mobile" for navigation
       Everything else gets desktop-style navigation */
    const isMobile = computed((): boolean => xs.value);

    return {
        isPhone,
        isTablet,
        isMobile,
    };
}
