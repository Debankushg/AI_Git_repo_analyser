import type { PendingAction } from "../../types";

interface Props {
  action: PendingAction;
  onResolve: (id: string, approve: boolean) => void;
}

const STYLE = {
  pending: "border-warn/50 bg-warn/5",
  approved: "border-ok/50 bg-ok/5",
  rejected: "border-gold/30 bg-subtle opacity-70",
};
const BADGE = {
  pending: "bg-warn/15 text-warn",
  approved: "bg-ok/15 text-ok",
  rejected: "bg-subtle text-muted",
};

export default function ActionApprovalCard({ action, onResolve }: Props) {
  return (
    <div className={`rounded-xl border p-3 ${STYLE[action.status]}`}>
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-semibold">{action.summary}</p>
        <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize ${BADGE[action.status]}`}>{action.status}</span>
      </div>
      <pre className="mt-2 max-h-40 overflow-auto rounded-lg bg-card p-2 font-mono text-[11px] leading-relaxed">{JSON.stringify(action.arguments, null, 2)}</pre>
      {action.status === "pending" && (
        <div className="mt-3 flex gap-2">
          <button onClick={() => onResolve(action.id, true)} className="btn-primary py-1.5 text-xs">
            Approve
          </button>
          <button onClick={() => onResolve(action.id, false)} className="btn-ghost py-1.5 text-xs">
            Reject
          </button>
        </div>
      )}
    </div>
  );
}
