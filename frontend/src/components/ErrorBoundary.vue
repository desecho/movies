<template>
  <div v-if="!hasError" class="error-boundary-content">
    <slot />
  </div>
  <div v-else class="error-boundary-fallback">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8" lg="6">
          <v-card class="error-card" elevation="4">
            <v-card-title class="error-title">
              <v-icon icon="mdi-alert-circle" color="error" size="large" class="mr-3" />
              Something went wrong
            </v-card-title>

            <v-card-text>
              <div class="error-message">
                <p class="text-body-1 mb-4">
                  {{ errorInfo.userMessage || "An unexpected error occurred. We're working to fix this issue." }}
                </p>

                <v-alert v-if="showDetails && errorInfo.details" type="info" variant="outlined" class="mb-4">
                  <div class="error-details">
                    <p><strong>Error Type:</strong> {{ errorInfo.type }}</p>
                    <p v-if="errorInfo.code"><strong>Code:</strong> {{ errorInfo.code }}</p>
                    <p v-if="errorInfo.context"><strong>Context:</strong> {{ errorInfo.context }}</p>
                    <p><strong>Time:</strong> {{ formatTimestamp(errorInfo.timestamp) }}</p>
                  </div>
                </v-alert>

                <div class="error-actions">
                  <v-btn
                    color="primary"
                    variant="elevated"
                    prepend-icon="mdi-refresh"
                    class="mr-2 mb-2"
                    @click="handleRetry"
                  >
                    Try Again
                  </v-btn>

                  <v-btn
                    color="secondary"
                    variant="outlined"
                    prepend-icon="mdi-home"
                    class="mr-2 mb-2"
                    @click="goHome"
                  >
                    Go Home
                  </v-btn>

                  <v-btn
                    color="info"
                    variant="text"
                    :prepend-icon="showDetails ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                    class="mr-2 mb-2"
                    @click="showDetails = !showDetails"
                  >
                    {{ showDetails ? "Hide Details" : "Show Details" }}
                  </v-btn>

                  <v-btn color="warning" variant="text" prepend-icon="mdi-bug" class="mb-2" @click="reportError">
                    Report Issue
                  </v-btn>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts" setup>
import { onErrorCaptured, ref } from "vue";
import { useRouter } from "vue-router";

import type { AppError } from "../utils/errorHandling";

import { $toast } from "../toast";
import { createAppError, ErrorSeverity } from "../utils/errorHandling";

interface Props {
  /** Custom fallback message for this boundary */
  fallbackMessage?: string;
  /** Context identifier for error reporting */
  context?: string;
  /** Whether to show retry button */
  allowRetry?: boolean;
  /** Whether to auto-reset after specified milliseconds */
  autoResetAfter?: number;
}

const props = withDefaults(defineProps<Props>(), {
  fallbackMessage: undefined,
  context: "ErrorBoundary",
  allowRetry: true,
  autoResetAfter: undefined,
});

const emit = defineEmits<{
  error: [error: AppError];
  retry: [];
  reset: [];
}>();

const router = useRouter();

const hasError = ref(false);
const errorInfo = ref<AppError>({} as AppError);
const showDetails = ref(false);
const retryCount = ref(0);

// Auto-reset timer
let autoResetTimer: ReturnType<typeof setTimeout> | null = null;

/**
 * Reset the error state
 */
function resetError(): void {
  hasError.value = false;
  errorInfo.value = {} as AppError;
  showDetails.value = false;
  retryCount.value = 0;

  if (autoResetTimer) {
    clearTimeout(autoResetTimer);
    autoResetTimer = null;
  }

  emit("reset");
}

/**
 * Handle any error within this boundary
 */
function handleErrorInternal(error: unknown, context?: string): void {
  const appError = createAppError(error, context || props.context, props.fallbackMessage);

  // Force high severity for boundary errors
  if (appError.severity < ErrorSeverity.HIGH) {
    appError.severity = ErrorSeverity.HIGH;
  }

  errorInfo.value = appError;
  hasError.value = true;

  // Emit error event for parent components
  emit("error", appError);

  // Setup auto-reset if configured
  if (props.autoResetAfter && props.autoResetAfter > 0) {
    autoResetTimer = setTimeout(() => {
      resetError();
    }, props.autoResetAfter);
  }

  // Log error details
  console.error("[ErrorBoundary] Error details:", {
    appError,
    context,
    timestamp: new Date().toISOString(),
  });
}

/**
 * Vue's error capture hook
 */
onErrorCaptured((error: Error, instance, info: string) => {
  console.error("[ErrorBoundary] Captured error:", { error, instance, info });

  handleErrorInternal(error, `${props.context}: ${info}`);

  // Return false to prevent the error from propagating further
  return false;
});

/**
 * Handle retry action
 */
function handleRetry(): void {
  retryCount.value++;

  if (retryCount.value > 3) {
    $toast.error("Too many retry attempts. Please refresh the page.");
    return;
  }

  resetError();
  emit("retry");

  $toast.success("Retrying...");
}

/**
 * Navigate to home page
 */
function goHome(): void {
  resetError();
  void router.push("/");
}

/**
 * Report error to support/logging service
 */
function reportError(): void {
  // Create error report
  const errorReport = {
    ...errorInfo.value,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
    retryCount: retryCount.value,
  };

  // Copy error details to clipboard
  const reportText = JSON.stringify(errorReport, null, 2);

  if (navigator.clipboard) {
    navigator.clipboard
      .writeText(reportText)
      .then(() => {
        $toast.success("Error details copied to clipboard. Please include this when reporting the issue.");
      })
      .catch(() => {
        $toast.error("Could not copy error details. Please take a screenshot of the error details below.");
        showDetails.value = true;
      });
  } else {
    $toast.error("Could not copy error details. Please take a screenshot of the error details below.");
    showDetails.value = true;
  }

  // TODO: Send to actual error reporting service
  console.log("[ErrorBoundary] Error report prepared:", errorReport);
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp: number): string {
  return new Date(timestamp).toLocaleString();
}

/**
 * Expose methods for programmatic error handling
 */
defineExpose({
  handleError: handleErrorInternal,
  resetError,
});
</script>

<style scoped>
.error-boundary-content {
  width: 100%;
  height: 100%;
}

.error-boundary-fallback {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.error-card {
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
}

.error-title {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 16px 16px 0 0;
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
}

.error-message {
  padding: 0.5rem;
}

.error-details {
  font-size: 0.9rem;
  font-family: "Courier New", monospace;
}

.error-details p {
  margin: 0.25rem 0;
  word-break: break-word;
}

.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

/* Dark theme support */
:deep(.v-theme--dark) .error-card {
  background-color: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.v-theme--dark) .error-details {
  color: #e2e8f0;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .error-boundary-fallback {
    padding: 1rem;
    min-height: 300px;
  }

  .error-title {
    padding: 1rem;
    font-size: 1.1rem;
  }

  .error-actions {
    flex-direction: column;
  }

  .error-actions .v-btn {
    width: 100%;
    margin: 0 0 0.5rem 0 !important;
  }
}
</style>
