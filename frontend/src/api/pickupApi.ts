import { request } from "./client";
import type { Pickup } from "./types";

export const pickupApi = {
  create: (token: string, body: Record<string, unknown>) =>
    request<Pickup>("/api/pickups", { method: "POST", body: JSON.stringify(body) }, token),
  get: (token: string, id: string) => request<Pickup>(`/api/pickups/${id}`, {}, token),
  status: (token: string, id: string, status: string) =>
    request<Pickup>(`/api/pickups/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }, token),
};
