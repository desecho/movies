<template>
  <div v-if="show" :class="containerClass">
    <div v-if="variant === 'overlay'" class="loading-overlay">
      <div class="loading-content">
        <LoadingSpinner :size="size" :color="color" />
        <p v-if="message" class="loading-message">{{ message }}</p>
        <p v-if="retryCount > 0" class="retry-message">Attempt {{ retryCount + 1 }}...</p>
      </div>
    </div>

    <div v-else-if="variant === 'inline'" class="loading-inline">
      <LoadingSpinner :size="size" :color="color" />
      <span v-if="message" class="loading-message">{{ message }}</span>
      <span v-if="retryCount > 0" class="retry-message"> (Attempt {{ retryCount + 1 }}) </span>
    </div>

    <div v-else-if="variant === 'skeleton'" class="loading-skeleton">
      <div v-for="line in skeletonLines" :key="line" class="skeleton-line" />
    </div>

    <div v-else class="loading-minimal">
      <LoadingSpinner :size="size" :color="color" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, defineComponent } from "vue";

interface Props {
  /** Whether to show the loading indicator */
  show: boolean;
  /** Loading indicator variant */
  variant?: "overlay" | "inline" | "minimal" | "skeleton";
  /** Size of the spinner */
  size?: "small" | "medium" | "large";
  /** Color of the spinner */
  color?: string;
  /** Loading message to display */
  message?: string;
  /** Current retry attempt (0-based) */
  retryCount?: number;
  /** Number of skeleton lines for skeleton variant */
  skeletonLines?: number;
  /** Additional CSS classes */
  class?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "minimal",
  size: "medium",
  color: "primary",
  message: "",
  retryCount: 0,
  skeletonLines: 3,
  class: "",
});

const containerClass = computed(() => {
  const base = `loading-container loading-${props.variant}`;
  return props.class ? `${base} ${props.class}` : base;
});

const LoadingSpinner = defineComponent({
  name: "LoadingSpinner",
  props: {
    size: {
      type: String,
      default: "medium",
      validator: (value: string) => ["small", "medium", "large"].includes(value),
    },
    color: {
      type: String,
      default: "primary",
    },
  },
  computed: {
    spinnerClass() {
      return `loading-spinner loading-spinner-${this.size}`;
    },
    spinnerSize() {
      switch (this.size) {
        case "small":
          return 20;
        case "large":
          return 48;
        default:
          return 32;
      }
    },
  },
  template: `
    <div :class="spinnerClass">
      <svg 
        :width="spinnerSize" 
        :height="spinnerSize" 
        viewBox="0 0 50 50" 
        class="loading-spinner-svg"
      >
        <circle
          cx="25"
          cy="25"
          r="20"
          fill="none"
          :stroke="color === 'primary' ? '#667eea' : color"
          stroke-width="4"
          stroke-linecap="round"
          stroke-dasharray="31.416"
          stroke-dashoffset="31.416"
          class="loading-spinner-circle"
        />
      </svg>
    </div>
  `,
});
</script>

<style scoped>
/* Container Variants */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  text-align: center;
  max-width: 300px;
}

.loading-inline {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
}

.loading-minimal {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

/* Messages */
.loading-message {
  margin: 0.75rem 0 0 0;
  font-size: 1rem;
  color: #6b7280;
  font-weight: 500;
}

.loading-inline .loading-message {
  margin: 0;
}

.retry-message {
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
  color: #9ca3af;
  font-style: italic;
}

.loading-inline .retry-message {
  margin: 0;
}

/* Spinner Styles */
.loading-spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner-svg {
  animation: loading-spin 2s linear infinite;
}

.loading-spinner-circle {
  animation: loading-dash 1.5s ease-in-out infinite;
}

@keyframes loading-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes loading-dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

/* Skeleton Loading */
.loading-skeleton {
  padding: 1rem;
  space-y: 0.75rem;
}

.skeleton-line {
  height: 1rem;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.skeleton-line:nth-child(1) {
  width: 80%;
}

.skeleton-line:nth-child(2) {
  width: 60%;
}

.skeleton-line:nth-child(3) {
  width: 90%;
}

.skeleton-line:last-child {
  margin-bottom: 0;
}

@keyframes skeleton-loading {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* Dark Theme */
:deep(.v-theme--dark) .loading-content {
  background: #1e293b;
  color: white;
}

:deep(.v-theme--dark) .loading-message {
  color: #cbd5e1;
}

:deep(.v-theme--dark) .retry-message {
  color: #94a3b8;
}

:deep(.v-theme--dark) .skeleton-line {
  background: linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%);
  background-size: 200% 100%;
}

/* Responsive */
@media (max-width: 768px) {
  .loading-content {
    padding: 1.5rem;
    max-width: 280px;
  }

  .loading-message {
    font-size: 0.9rem;
  }

  .loading-inline {
    padding: 0.75rem;
    gap: 0.5rem;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner-svg,
  .loading-spinner-circle {
    animation: none;
  }

  .loading-spinner-circle {
    stroke-dasharray: none;
    stroke-dashoffset: 0;
  }

  .skeleton-line {
    animation: none;
    background: #e0e0e0;
  }
}

/* Focus styles for accessibility */
.loading-container:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}
</style>
