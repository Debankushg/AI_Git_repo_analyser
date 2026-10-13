import { useEffect } from "react";
import type { RepoFile } from "../../types";
import { fileName } from "../../utils/fileUtils";
import ErrorAlert from "../common/ErrorAlert";
import Spinner from "../common/Spinner";
import FileViewer from "./FileViewer";

interface Props {
  path: string;
  file: RepoFile | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  onClose: () => void;
}

/** Large reading view that opens when a file is clicked in the explorer. Closes with Esc / outside click. */
export default function FileModal({ path, file, loading, error, onRetry, onClose }: Props) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-3 backdrop-blur-sm sm:p-8" onClick={onClose}>
      <div className="gold-border w-full max-w-6xl rounded-2xl p-4 shadow-gold" onClick={(e) => e.stopPropagation()} role="dialog" aria-label={fileName(path)}>
        {loading ? (
          <div className="flex items-center gap-2 py-10 text-sm text-muted">
            <Spinner /> Loading {fileName(path)}…
          </div>
        ) : file ? (
          <FileViewer file={file} expanded onClose={onClose} />
        ) : (
          <div className="space-y-3 py-2">
            <ErrorAlert error={error ?? "Could not load file"} onRetry={onRetry} />
            <button className="btn-ghost" onClick={onClose}>
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
