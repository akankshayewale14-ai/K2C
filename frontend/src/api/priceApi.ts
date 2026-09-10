import { request } from "./client";
import type { MapConfig, Price } from "./types";

export const priceApi = {
  list: (material?: string) => request<Price[]>(`/api/prices${material ? `?material=${material}` : ""}`),
  one: (material: string) => request<Price>(`/api/prices/${material}`),
  materials: () => request<{ id: string; slug: string; name: string; unit: string; category: string }[]>("/api/materials"),
  mapConfig: () => request<MapConfig>("/api/map/config"),
};
