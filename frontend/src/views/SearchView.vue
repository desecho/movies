<template>
    <v-container>
        <v-row>
            <v-col cols="6">
                <v-form
                    ref="form"
                    v-model="isFormValid"
                    lazy-validation
                    @submit.prevent="search"
                >
                    <v-text-field
                        v-model="query"
                        label="Search"
                        variant="solo"
                        :hide-details="true"
                        :rules="[rules.required]"
                        class="mr-5"
                        :autofocus="true"
                    ></v-text-field>
                </v-form>
            </v-col>
            <v-col cols="3" class="mt-2">
                <v-btn color="primary" :disabled="!isFormValid" @click="search">
                    Search
                </v-btn>
            </v-col>
            <v-col cols="3" class="mt-2">
                <v-select
                    v-model="type"
                    :items="['Movie', 'Actor', 'Director']"
                    density="compact"
                    @update:model-value="onTypeChange"
                >
                </v-select>
                <v-checkbox
                    v-model="popularOnly"
                    class="ma-0 pa-0"
                    density="compact"
                    hide-details
                    label="Show only popular"
                ></v-checkbox>
                <v-checkbox
                    v-model="sortByDate"
                    class="ma-0 pa-0"
                    density="compact"
                    hide-details
                    label="Sort by date"
                ></v-checkbox>
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="12">
                <MoviesList :movies="movies" />
            </v-col>
        </v-row>
    </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { ref } from "vue";

import type { MoviePreview } from "../types";
import type { AxiosError } from "axios";
import type { Ref } from "vue";

import MoviesList from "../components/MoviesList.vue";
import { useFormValidation } from "../composables/formValidation";
import { getUrl, rulesHelper } from "../helpers";
import { $toast } from "../toast";

const rules = rulesHelper;

const isFormValid = ref(false);
const movies: Ref<MoviePreview[]> = ref([]);
const query = ref("");
const type = ref("Movie");
const typeCode = ref("movie");
const popularOnly = ref(true);
const sortByDate = ref(false);

const { form, isValid } = useFormValidation();

function onTypeChange(type_: string): void {
    switch (type_) {
        case "Movie":
            typeCode.value = "movie";
            break;
        case "Actor":
            typeCode.value = "actor";
            break;
        case "Director":
            typeCode.value = "director";
            break;
        default:
            typeCode.value = "movie";
    }
}

async function search(): Promise<void> {
    if (!(await isValid())) {
        return;
    }
    const options = {
        popularOnly: popularOnly.value,
        sortByDate: sortByDate.value,
    };
    const data = {
        query: query.value,
        type: typeCode.value,
        options: JSON.stringify(options),
    };

    axios
        .get(getUrl("search/"), { params: data })
        .then((response) => {
            const ms: MoviePreview[] = response.data as MoviePreview[];
            if (ms.length === 0) {
                $toast.info("Nothing has been found");
            }
            ms.forEach((m: MoviePreview) => {
                m.hidden = false;
            });

            movies.value = ms;
        })
        .catch((error: AxiosError) => {
            console.log(error);
            $toast.error("Search error");
        });
}
</script>
