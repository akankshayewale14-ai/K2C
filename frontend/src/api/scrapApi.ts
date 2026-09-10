import { request } from "./client";
import type { Scrap } from "./types";

export const scrapApi = {
  create: (token: string, body: Record<string, unknown>) =>
    request<Scrap>("/api/scrap", { method: "POST", body: JSON.stringify(body) }, token),
  get: (token: string, id: string) => request<Scrap>(`/api/scrap/${id}`, {}, token),
  list: (token: string) => request<Scrap[]>("/api/scrap", {}, token),
  upload: async (token: string, id: string, files: File[]) => {
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    return request<{ uploaded: number }>(`/api/scrap/${id}/images`, { method: "POST", body: form }, token);
  },
  identify: (token: string, id: string) => request<Scrap>(`/api/scrap/${id}/identify`, { method: "POST" }, token),
  quantity: (token: string, id: string, body: Record<string, unknown>) =>
    request<Scrap>(`/api/scrap/${id}/quantity`, { method: "POST", body: JSON.stringify(body) }, token),
};
