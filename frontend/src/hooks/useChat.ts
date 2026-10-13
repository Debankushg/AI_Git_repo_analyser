import { useCallback, useEffect, useState } from "react";
import { approveAction, rejectAction, sendChat } from "../services/chatService";
import type { ChatMessage, PendingAction } from "../types";

export function useChat(repo: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [actions, setActions] = useState<PendingAction[]>([]);
  const [toolCalls, setToolCalls] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMessages([]);
    setActions([]);
    setToolCalls([]);
  }, [repo]);

  const run = useCallback(
    async (history: ChatMessage[]) => {
      if (!repo) return;
      setLoading(true);
      setError(null);
      try {
        const res = await sendChat(repo, history);
        setMessages([...history, { role: "assistant", content: res.reply || "(No text response. Check the Action Approval panel.)" }]);
        setToolCalls(res.tool_calls);
        setActions((prev) => [...prev, ...res.pending_actions]);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    },
    [repo],
  );

  const send = useCallback(
    async (text: string) => {
      if (!repo || !text.trim()) return;
      const next: ChatMessage[] = [...messages, { role: "user", content: text }];
      setMessages(next);
      await run(next);
    },
    [repo, messages, run],
  );

  const retry = useCallback(() => run(messages), [run, messages]);
  const dismissError = useCallback(() => setError(null), []);

  const resolve = useCallback(async (id: string, approve: boolean) => {
    try {
      const updated = await (approve ? approveAction(id) : rejectAction(id));
      setActions((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  return { messages, actions, toolCalls, loading, error, send, retry, dismissError, resolve };
}
