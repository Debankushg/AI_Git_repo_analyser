import { useAsync } from "../../hooks/useAsync";
import { getCommits } from "../../services/repositoryService";
import { fullDate, timeAgo } from "../../utils/dateUtils";
import Avatar from "../common/Avatar";
import EmptyState from "../common/EmptyState";
import ErrorAlert from "../common/ErrorAlert";
import { CommitIcon } from "../common/Icons";
import Spinner from "../common/Spinner";

export default function CommitList({ repo }: { repo: string }) {
  const { data, loading, error, retry } = useAsync(() => getCommits(repo), [repo]);
  if (loading) return <Spinner />;
  if (error) return <ErrorAlert error={error} onRetry={retry} />;
  if (!data?.length) return <EmptyState icon={<CommitIcon className="h-6 w-6" />} title="No commits yet" />;

  return (
    <ul className="space-y-2">
      {data.map((c) => {
        const [title, ...rest] = c.message.split("\n");
        return (
          <li key={c.sha} className="rounded-xl border border-gold/30 p-3 transition hover:border-gold hover:bg-subtle/60">
            <a href={c.html_url ?? undefined} target="_blank" rel="noreferrer" className="block">
              <p className="line-clamp-2 text-sm font-medium" title={rest.join("\n").trim() || undefined}>
                {title}
              </p>
              <div className="mt-2 flex items-center gap-2 text-xs text-muted">
                <Avatar src={c.avatar_url} name={c.author_name} className="h-5 w-5" />
                <span className="truncate font-medium text-fg/80">{c.author_name}</span>
                <span aria-hidden>·</span>
                <time dateTime={c.date ?? undefined} title={fullDate(c.date)} className="whitespace-nowrap">
                  {timeAgo(c.date)}
                </time>
                <code className="ml-auto rounded bg-gold/15 px-1.5 py-0.5 font-mono text-[10px] text-gold">{c.sha.slice(0, 7)}</code>
              </div>
            </a>
          </li>
        );
      })}
    </ul>
  );
}
