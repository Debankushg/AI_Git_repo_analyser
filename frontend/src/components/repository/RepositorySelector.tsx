import { useAsync } from "../../hooks/useAsync";
import type { Repository } from "../../types";
import { getRepositories } from "../../services/repositoryService";

interface Props {
  value: string | null;
  extra?: Repository[]; // repositories opened from a pasted link
  onChange: (repo: string) => void;
}

export default function RepositorySelector({ value, extra = [], onChange }: Props) {
  const { data, loading, error, retry } = useAsync(getRepositories, []);
  return (
    <div className="flex items-center gap-2">
      <select
        aria-label="Repository"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        disabled={loading}
        className="input w-56 sm:w-72"
      >
        <option value="" disabled>
          {loading ? "Loading repositories…" : "Select a repository"}
        </option>
        {[...extra.filter((x) => !data?.some((d) => d.full_name === x.full_name)), ...(data ?? [])].map((r) => (
          <option key={r.full_name} value={r.full_name}>
            {r.full_name}
            {r.private ? "  (private)" : ""}
          </option>
        ))}
      </select>
      {error && (
        <button onClick={retry} className="rounded-md border border-danger/40 bg-danger/10 px-2 py-1 text-xs font-medium text-danger animate-shake" title={error}>
          Failed to load · Retry
        </button>
      )}
    </div>
  );
}
