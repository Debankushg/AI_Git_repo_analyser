import type { RepositoryDetail } from "../../types";
import { formatCount } from "../../utils/numberUtils";
import Avatar from "../common/Avatar";
import { BranchIcon, ForkIcon, LockIcon, StarIcon } from "../common/Icons";

const chip = "inline-flex items-center gap-1 rounded-full bg-gold/15 px-2 py-0.5 text-[11px] font-medium text-gold";
const PROVIDER_LABEL = { github: "GitHub", gitlab: "GitLab", git: "Git" } as const;

/** Summary of the selected repository, detected automatically from its link. */
export default function RepositoryInfoBar({ detail, activeRef }: { detail: RepositoryDetail | null; activeRef?: string | null }) {
  if (!detail) return <div className="mx-4 mt-4 h-[58px] animate-pulse rounded-2xl border border-gold/30 bg-card/60" aria-hidden />;

  const host = detail.provider === "git" ? detail.id.split("/")[0] : null; // e.g. git.savannah.gnu.org
  return (
    <div className="gold-border mx-4 mt-4 flex animate-fade-up flex-wrap items-center gap-x-4 gap-y-2 rounded-2xl px-4 py-3 shadow-gold">
      <Avatar src={detail.owner_avatar_url} name={detail.full_name} className="h-9 w-9" />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <a href={detail.html_url ?? undefined} target="_blank" rel="noreferrer" className="truncate text-sm font-semibold hover:text-gold">
            {detail.full_name}
          </a>
          <span className={chip}>{PROVIDER_LABEL[detail.provider]}{host ? ` · ${host}` : ""}</span>
          <span className={chip}>
            {detail.private && <LockIcon className="h-3 w-3" />}
            {detail.private ? "Private" : "Public"}
          </span>
        </div>
        <p className="truncate text-xs text-muted">{detail.description ?? "No description provided"}</p>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
        {detail.language && <span className={chip}>{detail.language}</span>}
        {detail.provider !== "git" && (
          <>
            <span className="inline-flex items-center gap-1" title="Stars">
              <StarIcon className="h-3.5 w-3.5 text-gold" /> {formatCount(detail.stars)}
            </span>
            <span className="inline-flex items-center gap-1" title="Forks">
              <ForkIcon className="h-3.5 w-3.5 text-gold" /> {formatCount(detail.forks)}
            </span>
          </>
        )}
        <span className="inline-flex items-center gap-1 font-mono" title={activeRef ? "Branch from link" : "Default branch"}>
          <BranchIcon className="h-3.5 w-3.5 text-gold" /> {activeRef ?? detail.default_branch ?? "—"}
        </span>
      </div>
    </div>
  );
}
