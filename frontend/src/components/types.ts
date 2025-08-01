import type { ListKey } from "../types";

export type GameIdsWithListKeys = Record<number, ListKey>;

export interface SortData {
    id: number;
    order: number;
}

export interface Switch {
    name: string;
    label: string;
}
