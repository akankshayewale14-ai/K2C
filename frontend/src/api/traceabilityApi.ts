import { request } from "./client";
import type { Trace } from "./types";

export const traceabilityApi = {
  get: (lotId: string) => request<Trace>(`/api/traceability/${encodeURIComponent(lotId)}`),
};
