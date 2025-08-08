import axios from "axios";

import type { ShareRequest, ShareResponse } from "../types";
import type { AxiosResponse } from "axios";

import { getUrl } from "../helpers";

export const shareService = {
    /**
     * Generate social media share URL
     */
    async generateShareUrl(
        recordId: number,
        platform: string = "twitter",
    ): Promise<string> {
        const payload: ShareRequest = { platform };
        const response: AxiosResponse<ShareResponse> =
            await axios.post<ShareResponse>(
                getUrl(`share/${recordId}/`),
                payload,
            );
        return response.data.share_url;
    },

    /**
     * Open share URL in new window
     */
    openShareWindow(shareUrl: string): void {
        window.open(
            shareUrl,
            "_blank",
            "width=600,height=400,scrollbars=yes,resizable=yes",
        );
    },
};
