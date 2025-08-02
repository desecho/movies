<template>
  <v-app>
    <v-main>
      <MenuComponent />
      <RouterView />
    </v-main>
    <FooterComponent />
  </v-app>
</template>

<script lang="ts" setup>
import FooterComponent from "./components/FooterComponent.vue";
import MenuComponent from "./components/MenuComponent.vue";
</script>
