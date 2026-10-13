import { useMemo, useState } from "react";
import { useAsync } from "../../hooks/useAsync";
import { getEndpoints } from "../../services/repositoryService";
import EmptyState from "../common/EmptyState";
import ErrorAlert from "../common/ErrorAlert";
import { ApiIcon } from "../common/Icons";
import Spinner from "../common/Spinner";

const CATEGORY_LABELS: Record<string, string> = {
  health: "Health",
  repositories: "Repositories & Files",
  issues: "Issues & Pull Requests",
  commits: "Commits",
  chat: "AI Chat",
  actions: "Action Approval",
  meta: "Meta",
};

const METHOD_STYLE: Record<string, string> = {
  GET: "bg-ok/15 text-ok",
  POST: "bg-gold/20 text-gold",
  PUT: "bg-warn/15 text-warn",
  PATCH: "bg-warn/15 text-warn",
  DELETE: "bg-danger/15 text-danger",
};

const label = (c: string) => CATEGORY_LABELS[c] ?? c.charAt(0).toUpperCase() + c.slice(1);

/** Highlights {path_params} inside a URL path. */
function PathText({ path }: { path: string }) {
  return (
    <code className="break-all font-mono text-[11px]">
      {path.split(/(\{[^}]+\})/).map((part, i) =>
        part.startsWith("{") ? (
          <span key={i} className="text-gold">
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </code>
  );
}

export default function EndpointsPanel() {
  const { data, loading, error, retry } = useAsync(getEndpoints, []);
  const [query, setQuery] = useState("");
  const [copied, setCopied] = useState<string | null>(null);

  const groups = useMemo(() => {
    const q = query.trim().toLowerCase();
    const map = new Map<string, NonNullable<typeof data>["endpoints"]>();
    for (const e of data?.endpoints ?? []) {
      if (q && !`${e.method} ${e.path} ${e.summary} ${label(e.category)}`.toLowerCase().includes(q)) continue;
      map.set(e.category, [...(map.get(e.category) ?? []), e]);
    }
    return [...map.entries()];
  }, [data, query]);

  const copy = async (path: string) => {
    try {
      await navigator.clipboard.writeText(path);
      setCopied(path);
      setTimeout(() => setCopied(null), 1200);
    } catch {
      /* clipboard unavailable */
    }
  };

  if (loading) return <Spinner />;
  if (error) return <ErrorAlert error={error} onRetry={retry} />;

  return (
    <div className="space-y-3">
      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={`Filter ${data?.total ?? 0} endpoints…`} className="input py-1.5 text-xs" aria-label="Filter endpoints" />
      {groups.length === 0 && <EmptyState icon={<ApiIcon className="h-6 w-6" />} title="No matching endpoints" />}
      {groups.map(([category, items]) => (
        <section key={category}>
          <h3 className="mb-1.5 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
            {label(category)}
            <span className="rounded-full bg-gold/15 px-1.5 py-0.5 text-[10px] text-gold">{items.length}</span>
          </h3>
          <ul className="space-y-1.5">
            {items.map((e) => (
              <li key={e.method + e.path}>
                <button onClick={() => copy(e.path)} title="Click to copy path" className="w-full rounded-lg border border-gold/25 p-2 text-left transition hover:border-gold hover:bg-subtle/60">
                  <div className="flex items-start gap-2">
                    <span className={`mt-px w-12 shrink-0 rounded px-1 py-0.5 text-center font-mono text-[10px] font-bold ${METHOD_STYLE[e.method] ?? "bg-subtle text-muted"}`}>{e.method}</span>
                    <PathText path={e.path} />
                  </div>
                  <p className="mt-1 pl-14 text-[11px] text-muted">{copied === e.path ? "Copied ✓" : e.summary}</p>
                </button>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
