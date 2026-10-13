import { useEffect, useState } from "react";
import type { LinkTarget } from "../../types";
import { useAsync } from "../../hooks/useAsync";
import { getContents, getFile } from "../../services/repositoryService";
import ErrorAlert from "../common/ErrorAlert";
import { FileIcon, FolderIcon } from "../common/Icons";
import FileModal from "./FileModal";
import Spinner from "../common/Spinner";

export interface ExplorerTarget extends LinkTarget {
  nonce: number; // changes on every pasted link so the same link can be re-applied
}

export default function RepositoryExplorer({ repo, target }: { repo: string; target: ExplorerTarget | null }) {
  const [path, setPath] = useState("");
  const [filePath, setFilePath] = useState<string | null>(null);
  const [ref, setRef] = useState<string | null>(null);
  const dir = useAsync(() => getContents(repo, path, ref), [repo, path, ref]);
  const file = useAsync(() => (filePath ? getFile(repo, filePath, ref) : Promise.resolve(null)), [repo, filePath, ref]);

  // Switching repository resets the view; a pasted link then jumps to the folder/file/branch it points to.
  useEffect(() => {
    setPath("");
    setFilePath(null);
    setRef(null);
  }, [repo]);

  useEffect(() => {
    if (!target) return;
    setRef(target.ref);
    if (target.kind === "blob") {
      setPath(target.path.split("/").slice(0, -1).join("/"));
      setFilePath(target.path);
    } else {
      setPath(target.kind === "tree" ? target.path : "");
      setFilePath(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target?.nonce]);

  const crumbs = path ? path.split("/") : [];

  return (
    <div className="space-y-3">
      <nav className="flex flex-wrap items-center gap-1 text-xs text-muted">
        <button onClick={() => setPath("")} className="font-medium text-gold hover:underline">
          {repo.split("/").pop()}
        </button>
        {ref && <span className="rounded bg-gold/15 px-1.5 py-0.5 font-mono text-[10px] text-gold">{ref}</span>}
        {crumbs.map((c, i) => (
          <span key={i} className="flex items-center gap-1">
            /
            <button onClick={() => setPath(crumbs.slice(0, i + 1).join("/"))} className="hover:text-fg hover:underline">
              {c}
            </button>
          </span>
        ))}
      </nav>
      {dir.loading && <Spinner />}
      {dir.error && <ErrorAlert error={dir.error} onRetry={dir.retry} />}
      <ul className="space-y-0.5">
        {dir.data
          ?.slice()
          .sort((a, b) => (a.type === b.type ? a.name.localeCompare(b.name) : a.type === "dir" ? -1 : 1))
          .map((e) => (
            <li key={e.path}>
              <button
                onClick={() => (e.type === "dir" ? setPath(e.path) : setFilePath(e.path))}
                className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm transition hover:bg-subtle"
              >
                {e.type === "dir" ? <FolderIcon className="h-4 w-4 text-gold" /> : <FileIcon className="h-4 w-4 text-muted" />}
                <span className="truncate">{e.name}</span>
              </button>
            </li>
          ))}
      </ul>
      {filePath && (
        <FileModal
          path={filePath}
          file={file.data?.path === filePath ? file.data : null}
          loading={file.loading || (!file.error && file.data?.path !== filePath)}
          error={file.error}
          onRetry={file.retry}
          onClose={() => setFilePath(null)}
        />
      )}
    </div>
  );
}
