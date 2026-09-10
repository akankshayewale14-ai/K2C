import { request } from "./client";
import type { Recycler } from "./types";

export const recyclerApi = {
  list: () => request<Recycler[]>("/api/recyclers"),
  lots: (token: string) => request<{ lot_id: string; status: string; weight: number | null; id: string }[]>("/api/recyclers/me/lots", {}, token),
};
