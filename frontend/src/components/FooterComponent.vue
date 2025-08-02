<template>
  <v-window>
    <v-window-item>
      <v-footer class="text-right float-right mt-5"
        ><div>
          Powered by
          <a href="https://www.themoviedb.org" target="_blank"><span class="powered-by-tmdb"></span></a><br />
          <router-link to="/about">About Movies</router-link><br />
          © 2013 - {{ new Date().getFullYear() }} {{ email }}. All rights reserved.
        </div>
      </v-footer>
    </v-window-item>
  </v-window>
</template>

<script lang="ts" setup>
import { ADMIN_EMAIL } from "../const";

const email = ADMIN_EMAIL;
</script>
