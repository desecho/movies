<script lang="ts" setup>
import axios from "axios";
import { onMounted } from "vue";

import type { AxiosError } from "axios";

import { getUrl } from "../helpers";
import { router } from "../router";
import { $toast } from "../toast";

const props = defineProps<{
    userId: number;
    timestamp: number;
    signature: string;
}>();

onMounted(() => {
    axios
        .post(getUrl("user/verify-registration/"), {
            // eslint-disable-next-line camelcase
            user_id: props.userId,
            timestamp: props.timestamp,
            signature: props.signature,
        })
        .then(() => {
            $toast.info("Registration verified");
            void router.push("/login");
        })
        .catch((error: AxiosError) => {
            console.log(error);
            $toast.error("Error verifying registration");
        });
});
</script>
