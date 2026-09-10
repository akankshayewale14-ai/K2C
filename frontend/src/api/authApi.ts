import { request } from "./client";
import type { Notification, TokenPair, User } from "./types";

export const authApi = {
  register: (body: Record<string, unknown>) => request<TokenPair>("/api/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (email: string, password: string) =>
    request<TokenPair>("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: (token: string) => request<User>("/api/me", {}, token),
  notifications: (token: string) => request<Notification[]>("/api/notifications", {}, token),
  reset: (email: string) => request<{ message: string }>("/api/auth/password-reset", { method: "POST", body: JSON.stringify({ email }) }),
};
