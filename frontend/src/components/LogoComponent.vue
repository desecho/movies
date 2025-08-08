<template>
  <div class="logo-container" :class="{ clickable: clickable }" @click="handleClick">
    <img
      v-if="!imageError"
      :src="logoSrc"
      :alt="altText"
      :class="logoClass"
      @error="onImageError"
      @load="onImageLoad"
    />
    <span v-if="showText || imageError" class="logo-text" :class="textClass">{{ text }}</span>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import { useThemeStore } from "../stores/theme";

interface Props {
  size?: "small" | "medium" | "large";
  showText?: boolean;
  text?: string;
  clickable?: boolean;
  navigateTo?: string;
  variant?: "default" | "white" | "compact";
}

const props = withDefaults(defineProps<Props>(), {
  size: "medium",
  showText: false,
  text: "MovieMunch",
  clickable: false,
  navigateTo: "/",
  variant: "default",
});

const router = useRouter();
const themeStore = useThemeStore();
const imageLoaded = ref(false);
const imageError = ref(false);

const logoSrc = computed(() => {
  return themeStore.isDark ? "/img/logo-dark.png" : "/img/logo.png";
});

const altText = "MovieMunch Logo";

const logoClass = computed(() => [
  "logo-image",
  `logo-${props.size}`,
  `logo-${props.variant}`,
  {
    "logo-loaded": imageLoaded.value,
    "logo-error": imageError.value,
  },
]);

const textClass = computed(() => [`text-${props.size}`, `text-${props.variant}`]);

function handleClick(): void {
  if (props.clickable && props.navigateTo) {
    void router.push(props.navigateTo);
  }
}

function onImageLoad(): void {
  imageLoaded.value = true;
  imageError.value = false;
}

function onImageError(): void {
  imageError.value = true;
  imageLoaded.value = false;
}
</script>

<style scoped>
.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.logo-container.clickable {
  cursor: pointer;
}

.logo-container.clickable:hover {
  transform: scale(1.02);
}

.logo-image {
  display: block;
  object-fit: contain;
  transition: all 0.3s ease;
  opacity: 1;
  border-radius: 35px;
}

.logo-image.logo-error {
  display: none;
}

/* Size variants */
.logo-small {
  height: 24px;
  width: auto;
}

.logo-medium {
  height: 32px;
  width: auto;
}

.logo-large {
  height: 65px;
  width: auto;
}

/* Logo variants */
.logo-white {
  /* Add subtle shadow for better visibility on gradient backgrounds */
  filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.3));
}

.logo-compact {
  height: 28px;
  width: auto;
}

/* Text styles */
.logo-text {
  font-weight: 700;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.text-small {
  font-size: 0.9rem;
}

.text-medium {
  font-size: 1.1rem;
}

.text-large {
  font-size: 1.5rem;
}

.text-default {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: #667eea; /* Fallback for browsers that don't support background-clip */
}

.text-white {
  color: white !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  background: none !important;
  -webkit-text-fill-color: white !important;
}

.text-compact {
  font-size: 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .logo-container {
    gap: 6px;
  }

  .logo-large {
    height: 36px;
  }

  .text-large {
    font-size: 1.3rem;
  }
}
</style>
