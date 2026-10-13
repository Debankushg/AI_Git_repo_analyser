import { FormEvent, useEffect, useRef, useState } from "react";
import type { ChatMessage } from "../../types";
import { SendIcon, SparkIcon } from "../common/Icons";
import ErrorAlert from "../common/ErrorAlert";
import Markdown from "../common/Markdown";
import Spinner from "../common/Spinner";

const SUGGESTIONS = [
  "Find the open bugs and pick the highest-priority one",
  "Which files might need changes to fix it?",
  "Summarize the latest commits",
];

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  onSend: (text: string) => void;
  onRetry: () => void;
  onDismissError: () => void;
}

export default function ChatPanel({ messages, loading, error, onSend, onRetry, onDismissError }: Props) {
  const [text, setText] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim() || loading) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="flex h-full min-h-[14rem] flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-3 py-6 text-center">
            <div className="grid h-12 w-12 place-items-center rounded-2xl gold-border text-gold">
              <SparkIcon className="h-6 w-6" />
            </div>
            <div>
              <p className="font-semibold">Ask anything about this repository</p>
              <p className="text-xs text-muted">I can read code, issues, pull requests and commits.</p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => onSend(s)} className="rounded-full border border-gold/40 bg-subtle px-3 py-1.5 text-xs transition hover:border-gold hover:text-gold">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className="flex justify-end">
              <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-md gold-fill px-4 py-2.5 text-sm font-medium text-[#2b1d03] shadow-gold">
                {m.content}
              </div>
            </div>
          ) : (
            <div key={i} className="flex gap-2.5">
              <div className="mt-0.5 gold-border grid h-7 w-7 shrink-0 place-items-center rounded-lg text-gold">
                <SparkIcon className="h-4 w-4" />
              </div>
              <div className="max-w-[88%] rounded-2xl rounded-tl-md border border-gold/30 bg-subtle px-4 py-2.5">
                <Markdown>{m.content}</Markdown>
              </div>
            </div>
          ),
        )}
        {loading && (
          <div className="flex items-center gap-2 pl-9 text-xs text-muted">
            <Spinner /> Thinking and calling GitHub tools…
          </div>
        )}
        {error && <ErrorAlert error={error} onRetry={onRetry} onDismiss={onDismissError} />}
        <div ref={endRef} />
      </div>
      <form onSubmit={submit} className="mt-3 flex gap-2">
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Ask about this repository…" className="input" />
        <button disabled={loading || !text.trim()} className="btn-primary" aria-label="Send">
          <SendIcon /> <span className="hidden sm:inline">Send</span>
        </button>
      </form>
    </div>
  );
}
