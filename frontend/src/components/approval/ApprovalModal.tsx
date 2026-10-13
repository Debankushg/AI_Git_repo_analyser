import { useEffect } from "react";
import type { PendingAction } from "../../types";
import { ShieldIcon, XIcon } from "../common/Icons";
import ApprovalPanel from "./ApprovalPanel";

interface Props {
  actions: PendingAction[];
  onResolve: (id: string, approve: boolean) => void;
  onClose: () => void;
}

/** Human-in-the-loop window: review what the AI wants to create before anything is written to GitHub. */
export default function ApprovalModal({ actions, onResolve, onClose }: Props) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-3 backdrop-blur-sm sm:p-8" onClick={onClose}>
      <div className="gold-border max-h-[85vh] w-full max-w-xl overflow-y-auto rounded-2xl p-4 shadow-gold animate-fade-up" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Action approval">
        <div className="mb-4 flex items-center gap-2">
          <ShieldIcon className="h-5 w-5 text-gold" />
          <h2 className="text-base font-semibold">Action Approval</h2>
          <button onClick={onClose} aria-label="Close" className="ml-auto h-7 w-7 rounded-md text-muted transition hover:bg-fg/10 hover:text-fg">
            <XIcon className="mx-auto h-4 w-4" />
          </button>
        </div>
        <ApprovalPanel actions={actions} onResolve={onResolve} />
      </div>
    </div>
  );
}
