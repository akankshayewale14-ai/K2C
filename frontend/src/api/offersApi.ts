import { request } from "./client";
import type { Offer } from "./types";

export const offersApi = {
  list: (token: string, listingId: string) => request<Offer[]>(`/api/offers?listing_id=${listingId}`, {}, token),
  accept: (token: string, id: string) => request<Offer>(`/api/offers/${id}/accept`, { method: "POST" }, token),
};
