import { request } from "./client";

export const adminApi = {
  users: (token: string) =>
    request<{ id: string; email: string; full_name: string; role: string; is_active: boolean }[]>("/api/admin/users", {}, token),
  verifications: (token: string) =>
    request<
      {
        id: string;
        status: string;
        authority_name: string | null;
        registration_number: string | null;
        verification_source: string | null;
        collector_id: string | null;
        recycler_id: string | null;
      }[]
    >("/api/admin/verifications", {}, token),
  review: (token: string, id: string, status: string, notes?: string) =>
    request<{ id: string; status: string }>(
      `/api/admin/verifications/${id}/review`,
      { method: "POST", body: JSON.stringify({ status, notes }) },
      token,
    ),
  audit: (token: string) =>
    request<{ id: string; action: string; entity: string; entity_id: string | null; created_at: string }[]>(
      "/api/admin/audit",
      {},
      token,
    ),
};
