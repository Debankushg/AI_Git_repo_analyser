import { useAsync } from "../../hooks/useAsync";
import { getPulls } from "../../services/repositoryService";
import { fullDate, timeAgo } from "../../utils/dateUtils";
import Avatar from "../common/Avatar";
import EmptyState from "../common/EmptyState";
import ErrorAlert from "../common/ErrorAlert";
import { PullIcon } from "../common/Icons";
import Spinner from "../common/Spinner";

interface Props {
  repo: string;
  label?: string; // "Pull requests" | "Merge requests"
  supported?: boolean; // false for hosts reached through plain git
}

export default function PullRequestList({ repo, label = "Pull requests", supported = true }: Props) {
  const { data, loading, error, retry } = useAsync(() => (supported ? getPulls(repo) : Promise.resolve([])), [repo, supported]);
  if (!supported)
    return <EmptyState icon={<PullIcon className="h-6 w-6" />} title={`${label} aren't available`} hint="This host is read through plain git, which has no pull request data. Files, commits and AI chat work fully." />;
  if (loading) return <Spinner />;
  if (error) return <ErrorAlert error={error} onRetry={retry} />;
  if (!data?.length) return <EmptyState icon={<PullIcon className="h-6 w-6" />} title={`No open ${label.toLowerCase()}`} />;
  return (
    <ul className="space-y-2">
      {data.map((p) => (
        <li key={p.number} className="rounded-xl border border-gold/30 p-3 transition hover:border-gold hover:bg-subtle/60">
          <a href={p.html_url} target="_blank" rel="noreferrer" className="block">
            <p className="flex gap-2 text-sm font-medium">
              <PullIcon className="mt-0.5 h-4 w-4 shrink-0 text-gold" />
              <span>
                {p.title} <span className="font-normal text-muted">#{p.number}</span>
              </span>
            </p>
            <div className="mt-2 flex items-center gap-2 pl-6 text-xs text-muted">
              {p.user?.login && <Avatar src={p.user.avatar_url} name={p.user.login} className="h-5 w-5" />}
              {p.user?.login && <span className="truncate font-medium text-fg/80">{p.user.login}</span>}
              {p.created_at && (
                <>
                  <span aria-hidden>·</span>
                  <time dateTime={p.created_at} title={fullDate(p.created_at)} className="whitespace-nowrap">
                    {timeAgo(p.created_at)}
                  </time>
                </>
              )}
              {p.draft && <span className="ml-auto rounded-full bg-subtle px-2 py-0.5 text-[10px] font-medium">Draft</span>}
            </div>
          </a>
        </li>
      ))}
    </ul>
  );
}
