import { ref } from "vue";

import { shareService } from "../services/shareService";
import { toast } from "../toast";

export function useSocialSharing(): {
    isSharing: typeof isSharing;
    shareToX: (recordId: number) => Promise<void>;
} {
    const isSharing = ref(false);

    async function shareToX(recordId: number): Promise<void> {
        if (isSharing.value) {
            return;
        }

        try {
            isSharing.value = true;
            const shareUrl = await shareService.generateShareUrl(
                recordId,
                "twitter",
            );
            shareService.openShareWindow(shareUrl);
        } catch (error: unknown) {
            console.error("Failed to share:", error);
            toast.error("Failed to generate share URL. Please try again.");
        } finally {
            // eslint-disable-next-line require-atomic-updates
            isSharing.value = false;
        }
    }

    return {
        isSharing,
        shareToX,
    };
}
