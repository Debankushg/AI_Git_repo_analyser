import EmptyState from "../common/EmptyState";
import { SparkIcon } from "../common/Icons";
import Markdown from "../common/Markdown";

const QUICK_PROMPTS = [
  "Find the open bugs and identify the highest-priority issue.",
  "Which files likely need changes to fix the top bug? Explain the likely cause.",
  "Summarize recent commits and what changed.",
  "Draft an issue for the most important problem you found.",
];

interface Props {
  lastReply: string | null;
  toolCalls: string[];
  disabled: boolean;
  onRun: (prompt: string) => void;
}

export default function AnalysisPanel({ lastReply, toolCalls, disabled, onRun }: Props) {
  return (
    <div className="space-y-4">
      <div className="grid gap-2 sm:grid-cols-2">
        {QUICK_PROMPTS.map((p) => (
          <button
            key={p}
            disabled={disabled}
            onClick={() => onRun(p)}
            className="rounded-xl border border-gold/40 bg-subtle/60 px-3 py-2 text-left text-xs transition hover:border-gold hover:text-gold disabled:cursor-not-allowed disabled:opacity-50"
          >
            {p}
          </button>
        ))}
      </div>
      {toolCalls.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          <span className="text-muted">Tools used:</span>
          {toolCalls.map((t, i) => (
            <span key={i} className="rounded-md bg-gold/15 px-1.5 py-0.5 font-mono text-gold">
              {t}
            </span>
          ))}
        </div>
      )}
      {lastReply ? (
        <div className="rounded-xl border border-gold/30 bg-subtle p-4">
          <Markdown>{lastReply}</Markdown>
        </div>
      ) : (
        <EmptyState icon={<SparkIcon className="h-6 w-6" />} title="No analysis yet" hint="Run a quick prompt or ask in the chat." />
      )}
    </div>
  );
}
