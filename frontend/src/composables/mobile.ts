import { computed } from "vue";
import { useDisplay } from "vuetify";

import type { ComputedRef } from "vue";

export function useMobile(): {
    isPhone: ComputedRef<boolean>;
    isMobile: ComputedRef<boolean>;
} {
    const { xs, sm } = useDisplay();
    const isPhone = computed((): boolean => xs.value);
    const isTablet = computed((): boolean => sm.value);
    const isMobile = computed((): boolean => isPhone.value || isTablet.value);

    return {
        isPhone,
        isMobile,
    };
}
