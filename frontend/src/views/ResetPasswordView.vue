<template>
    <v-container>
        <v-row class="text-center">
            <v-col class="mb-4" cols="12">
                <v-form
                    v-if="!isLoggedIn"
                    ref="form"
                    v-model="isFormValid"
                    lazy-validation
                    @submit.prevent="onSubmit"
                >
                    <v-text-field
                        v-model="password"
                        variant="solo"
                        :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                        :rules="[rules.required]"
                        :type="showPassword ? 'text' : 'password'"
                        label="Password"
                        @click:append="showPassword = !showPassword"
                        @keyup.enter="onSubmit"
                    ></v-text-field>
                    <div
                        class="d-flex justify-space-around align-center flex-column flex-md-row"
                    >
                        <v-btn
                            color="primary"
                            :disabled="!isFormValid"
                            @click="onSubmit"
                            >Reset password</v-btn
                        >
                    </div>
                </v-form>
                <p v-if="isLoggedIn">You are already logged in.</p>
            </v-col>
        </v-row>
    </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { ref } from "vue";

import type { AxiosError } from "axios";

import { useFormValidation } from "../composables/formValidation";
import { getUrl, rulesHelper } from "../helpers";
import { router } from "../router";
import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";

const rules = rulesHelper;

const props = defineProps<{
    userId: number;
    timestamp: number;
    signature: string;
}>();

const password = ref("");
const showPassword = ref(false);
const isFormValid = ref(false);

const { user } = useAuthStore();
const isLoggedIn = user.isLoggedIn;

const { form, isValid } = useFormValidation();

async function onSubmit(): Promise<void> {
    if (!(await isValid())) {
        return;
    }
    axios
        .post(getUrl("user/reset-password/"), {
            // eslint-disable-next-line camelcase
            user_id: props.userId,
            timestamp: props.timestamp,
            signature: props.signature,
            password: password.value,
        })
        .then(() => {
            $toast.success("Password reset is successful");
            void router.push("/login");
        })
        .catch((error: AxiosError) => {
            console.log(error);
            $toast.error("Error resetting password");
        });
}
</script>
