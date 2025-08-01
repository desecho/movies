import { ref } from "vue";

import type { Form } from "./types";
import type { Ref } from "vue";

export function useFormValidation(): {
    form: Ref<Form | null>;
    isValid: () => Promise<boolean>;
} {
    const form = ref(null) as Ref<Form | null>;

    async function isValid(): Promise<boolean> {
        if (form.value !== null) {
            const result = await form.value.validate();
            return result.valid;
        }
        return false;
    }

    return {
        form,
        isValid,
    };
}
