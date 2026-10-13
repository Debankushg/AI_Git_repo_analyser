import type { PendingAction } from "../../types";
import EmptyState from "../common/EmptyState";
import { ShieldIcon } from "../common/Icons";
import ActionApprovalCard from "./ActionApprovalCard";

interface Props {
  actions: PendingAction[];
  onResolve: (id: string, approve: boolean) => void;
}

export default function ApprovalPanel({ actions, onResolve }: Props) {
  if (!actions.length)
    return <EmptyState icon={<ShieldIcon className="h-6 w-6" />} title="Nothing to approve" hint="Issues and draft PRs the AI proposes appear here for your review." />;
  return (
    <div className="space-y-3">
      {actions.map((a) => (
        <ActionApprovalCard key={a.id} action={a} onResolve={onResolve} />
      ))}
    </div>
  );
}
