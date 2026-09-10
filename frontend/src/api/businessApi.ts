import { request } from "./client";
import type { Bulk } from "./types";

export const businessApi = {
  create: (token: string, body: Record<string, unknown>) =>
    request<Bulk>("/api/business/bulk-requests", { method: "POST", body: JSON.stringify(body) }, token),
  get: (token: string, id: string) => request<Bulk>(`/api/business/bulk-requests/${id}`, {}, token),
  offers: (token: string, id: string) => request<{ id: string; amount: number; notes: string | null }[]>(`/api/business/bulk-requests/${id}/offers`, {}, token),
};
