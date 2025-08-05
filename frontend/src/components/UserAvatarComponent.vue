<template>
  <v-avatar :size="size" :class="avatarClass" v-bind="$attrs">
    <v-img v-if="avatarUrl" :src="avatarUrl" :alt="altText" cover :class="imageClass" />
    <v-icon v-else :size="iconSize" :icon="defaultIcon" :class="iconClass" />
  </v-avatar>
</template>

<script lang="ts" setup>
import { computed } from "vue";

interface Props {
  avatarUrl?: string | null;
  username?: string;
  size?: string | number;
  variant?: "default" | "outlined" | "elevated";
  defaultIcon?: string;
}

const props = withDefaults(defineProps<Props>(), {
  avatarUrl: null,
  username: "User",
  size: 40,
  variant: "default",
  defaultIcon: "mdi-account-circle",
});

// Computed properties
const altText = computed(() => `${props.username} avatar`);

const iconSize = computed(() => {
  const size = typeof props.size === "string" ? parseInt(props.size, 10) : props.size;
  return Math.max(size * 0.6, 20);
});

const avatarClass = computed(() => {
  const classes = ["user-avatar"];

  if (props.variant === "outlined") {
    classes.push("user-avatar--outlined");
  } else if (props.variant === "elevated") {
    classes.push("user-avatar--elevated");
  }

  return classes;
});

const imageClass = computed(() => {
  return "user-avatar__image";
});

const iconClass = computed(() => {
  return "user-avatar__icon";
});
</script>

<style scoped>
.user-avatar {
  transition: all 0.2s ease;
}

.user-avatar--outlined {
  border: 2px solid rgb(var(--v-theme-outline));
}

.user-avatar--elevated {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-avatar:hover {
  transform: scale(1.05);
}

.user-avatar__image {
  transition: all 0.2s ease;
}

.user-avatar__icon {
  color: rgb(var(--v-theme-on-surface-variant));
}

/* Size-specific styles */
.user-avatar[style*="width: 24px"],
.user-avatar[style*="width: 32px"] {
  /* Small avatars don't need hover effects */
}

.user-avatar[style*="width: 24px"]:hover,
.user-avatar[style*="width: 32px"]:hover {
  transform: none;
}
</style>
