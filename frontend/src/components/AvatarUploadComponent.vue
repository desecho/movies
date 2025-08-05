<template>
  <div class="avatar-upload">
    <v-card class="elevation-2 pa-4">
      <v-card-title class="text-h6 mb-2">Profile Avatar</v-card-title>

      <!-- Current Avatar Display -->
      <div class="current-avatar mb-4 text-center">
        <v-avatar :size="120" class="mb-2">
          <v-img v-if="currentAvatarUrl" :src="currentAvatarUrl" :alt="username + ' avatar'" cover />
          <v-icon v-else size="60" icon="mdi-account-circle" />
        </v-avatar>
        <div class="text-body-2 text-medium-emphasis">
          {{ currentAvatarUrl ? "Current Avatar" : "No Avatar Set" }}
        </div>
      </div>

      <!-- File Upload Area -->
      <div
        class="upload-area mb-4"
        :class="{ 'drag-over': isDragOver, 'has-error': hasError }"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleDrop"
        @click="$refs.fileInput?.click()"
      >
        <input ref="fileInput" type="file" accept=".jpg,.jpeg,.png" style="display: none" @change="handleFileSelect" />

        <div class="upload-content">
          <v-icon size="48" icon="mdi-cloud-upload" class="mb-2" />
          <div class="text-body-1 mb-1">
            {{ isDragOver ? "Drop image here" : "Click to upload or drag and drop" }}
          </div>
          <div class="text-body-2 text-medium-emphasis">JPEG or PNG only, max 4,096 × 4,096 pixels</div>
        </div>
      </div>

      <!-- Preview Area -->
      <div v-if="previewUrl" class="preview-area mb-4">
        <v-card variant="outlined" class="pa-2">
          <div class="text-body-2 mb-2">Preview:</div>
          <v-avatar :size="80">
            <v-img :src="previewUrl" cover />
          </v-avatar>
          <div class="text-body-2 mt-2">{{ selectedFile?.name }} ({{ formatFileSize(selectedFile?.size || 0) }})</div>
        </v-card>
      </div>

      <!-- Error Messages -->
      <v-alert v-if="errorMessage" type="error" variant="tonal" class="mb-4" :text="errorMessage" />

      <!-- Action Buttons -->
      <v-card-actions class="px-0">
        <v-btn v-if="selectedFile" color="primary" :loading="isUploading" @click="uploadAvatar">
          <v-icon start icon="mdi-upload" />
          Upload Avatar
        </v-btn>

        <v-btn
          v-if="currentAvatarUrl && !selectedFile"
          color="error"
          variant="outlined"
          :loading="isDeleting"
          @click="deleteAvatar"
        >
          <v-icon start icon="mdi-delete" />
          Remove Avatar
        </v-btn>

        <v-btn v-if="selectedFile" variant="text" @click="clearSelection"> Cancel </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref } from "vue";

import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";

const authStore = useAuthStore();

// Component state
const selectedFile = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const isDragOver = ref(false);
const isUploading = ref(false);
const isDeleting = ref(false);
const errorMessage = ref<string | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

// Computed properties
const currentAvatarUrl = computed(() => authStore.user.avatarUrl);
const username = computed(() => authStore.user.username || "User");
const hasError = computed(() => Boolean(errorMessage.value));

// File validation
function validateFile(file: File): string | null {
  // Check file type
  const allowedTypes = ["image/jpeg", "image/jpg", "image/png"];
  if (!allowedTypes.includes(file.type)) {
    return "Please select a JPEG or PNG image file.";
  }

  // Check file size (10MB limit for safety)
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    return "File size must be less than 10MB.";
  }

  return null;
}

// Check image dimensions
async function checkImageDimensions(file: File): Promise<string | null> {
  return new Promise((resolve) => {
    const img = new Image();
    const url = URL.createObjectURL(file);

    img.onload = (): void => {
      URL.revokeObjectURL(url);
      const maxDimension = 4096;

      if (img.width > maxDimension || img.height > maxDimension) {
        const message =
          `Image dimensions must not exceed ${maxDimension} × ${maxDimension} pixels. ` +
          `Your image is ${img.width} × ${img.height}.`;
        resolve(message);
      } else {
        resolve(null);
      }
    };

    img.onerror = (): void => {
      URL.revokeObjectURL(url);
      resolve("Invalid image file.");
    };

    img.src = url;
  });
}

// Process selected file
async function processFile(file: File): Promise<void> {
  errorMessage.value = null;

  // Basic validation
  const basicError = validateFile(file);
  if (basicError) {
    errorMessage.value = basicError;
    return;
  }

  // Check dimensions
  const dimensionError = await checkImageDimensions(file);
  if (dimensionError) {
    errorMessage.value = dimensionError;
    return;
  }

  // File is valid
  selectedFile.value = file;
  previewUrl.value = URL.createObjectURL(file);
}

// Handle file selection
async function handleFileSelect(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    await processFile(file);
  }
}

// Handle drag and drop
async function handleDrop(event: DragEvent): Promise<void> {
  isDragOver.value = false;
  const file = event.dataTransfer?.files[0];
  if (file) {
    await processFile(file);
  }
}

// Clear selection
function clearSelection(): void {
  selectedFile.value = null;
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = null;
  }
  errorMessage.value = null;

  // Reset file input
  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

// Upload avatar
async function uploadAvatar(): Promise<void> {
  if (!selectedFile.value) {
    return;
  }

  isUploading.value = true;
  errorMessage.value = null;

  try {
    await authStore.uploadAvatar(selectedFile.value);
    $toast.success("Avatar uploaded successfully!");
    clearSelection();
  } catch (error) {
    console.error("Avatar upload error:", error);
    errorMessage.value = "Failed to upload avatar. Please try again.";
  } finally {
    isUploading.value = false;
  }
}

// Delete avatar
async function deleteAvatar(): Promise<void> {
  isDeleting.value = true;
  errorMessage.value = null;

  try {
    await authStore.deleteAvatar();
    $toast.success("Avatar removed successfully!");
  } catch (error) {
    console.error("Avatar delete error:", error);
    errorMessage.value = "Failed to remove avatar. Please try again.";
  } finally {
    isDeleting.value = false;
  }
}

// Format file size
function formatFileSize(bytes: number): string {
  if (bytes === 0) {
    return "0 Bytes";
  }
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`;
}
</script>

<style scoped>
.avatar-upload {
  max-width: 400px;
  margin: 0 auto;
}

.upload-area {
  border: 2px dashed rgb(var(--v-theme-outline));
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: rgb(var(--v-theme-surface-variant), 0.1);
}

.upload-area:hover {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgb(var(--v-theme-primary), 0.05);
}

.upload-area.drag-over {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgb(var(--v-theme-primary), 0.1);
  transform: scale(1.02);
}

.upload-area.has-error {
  border-color: rgb(var(--v-theme-error));
  background-color: rgb(var(--v-theme-error), 0.05);
}

.upload-content {
  pointer-events: none;
}

.preview-area {
  text-align: center;
}

.current-avatar {
  position: relative;
}
</style>
