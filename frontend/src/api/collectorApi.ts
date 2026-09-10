import { request } from "./client";
import type { Collector, MarketRequest } from "./types";

export const collectorApi = {
  list: () => request<Collector[]>("/api/collectors"),
  marketRequests: (token: string) => request<MarketRequest[]>("/api/scrap/marketplace", {}, token),
  dashboard: (token: string) => request<Record<string, unknown>>("/api/collectors/me/dashboard", {}, token),
  route: (token: string) => request<Record<string, unknown>>("/api/collectors/me/route", { method: "POST" }, token),
};
