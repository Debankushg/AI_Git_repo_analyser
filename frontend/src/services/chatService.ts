import type { ChatMessage, ChatResponse, PendingAction } from "../types";
import { api } from "./apiClient";

export const sendChat = (repo: string, messages: ChatMessage[]) =>
  api<ChatResponse>("/chat", { method: "POST", body: JSON.stringify({ repo, messages }) });
export const approveAction = (id: string) =>
  api<PendingAction>(`/actions/${id}/approve`, { method: "POST" });
export const rejectAction = (id: string) =>
  api<PendingAction>(`/actions/${id}/reject`, { method: "POST" });
