// eslint-disable-next-line import/no-unassigned-import
import "axios";

declare module "axios" {
    interface InternalAxiosRequestConfig {
        metadata?: {
            startTime: number;
            requestId: string;
        };
    }
}
