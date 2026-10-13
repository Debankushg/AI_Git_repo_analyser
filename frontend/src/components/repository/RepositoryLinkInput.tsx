import { FormEvent, useState } from "react";
import { resolveRepositoryLink } from "../../services/repositoryService";
import type { ResolveResponse } from "../../types";
import ErrorAlert from "../common/ErrorAlert";
import { LinkIcon } from "../common/Icons";
import Spinner from "../common/Spinner";

interface Props {
  onResolved: (result: ResolveResponse) => void;
}

const LOOKS_LIKE_REPO = /^(https?:\/\/|ssh:\/\/|git@)|\.git$|^[\w-]+(\.[\w-]+)+\/\S+|^[\w.-]+\/[\w.-]+$/i;

/** Paste any git link (GitHub, GitLab, Bitbucket, Azure, self-hosted, ssh, .git...) and the repo is detected and opened. */
export default function RepositoryLinkInput({ onResolved }: Props) {
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (raw: string) => {
    if (!raw.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      onResolved(await resolveRepositoryLink(raw));
      setValue("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    void submit(value);
  };

  return (
    <div className="relative">
      <form onSubmit={onSubmit} className="flex items-center gap-2">
        <div className="relative">
          <LinkIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gold" />
          <input
            value={value}
            onChange={(e) => {
              setValue(e.target.value);
              if (error) setError(null);
            }}
            onPaste={(e) => {
              const text = e.clipboardData.getData("text");
              if (LOOKS_LIKE_REPO.test(text.trim())) {
                e.preventDefault();
                setValue(text.trim());
                void submit(text); // auto-detect on paste
              }
            }}
            placeholder="Paste any git repo link…"
            aria-label="Git repository link"
            className="input w-52 pl-9 sm:w-72 lg:w-80"
          />
        </div>
        <button className="btn-primary h-9" disabled={loading || !value.trim()}>
          {loading ? <Spinner /> : "Open"}
        </button>
      </form>
      {error && (
        <div className="absolute right-0 top-full z-30 mt-2 w-[min(26rem,90vw)]">
          <ErrorAlert error={error} onDismiss={() => setError(null)} />
        </div>
      )}
    </div>
  );
}
