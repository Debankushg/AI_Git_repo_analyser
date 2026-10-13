import { useEffect, useState } from "react";
import type { RepoFile } from "../../types";
import { fileName, formatBytes, getLanguage, isMarkdown } from "../../utils/fileUtils";
import EmptyState from "../common/EmptyState";
import { FileIcon } from "../common/Icons";
import Markdown from "../common/Markdown";
import CodeView from "./CodeView";

interface Props {
  file: RepoFile;
  expanded?: boolean;
  onBack?: () => void;
  onExpand?: () => void;
  onClose?: () => void;
}

export default function FileViewer({ file, expanded, onBack, onExpand, onClose }: Props) {
  const md = isMarkdown(file.path);
  const [mode, setMode] = useState<"preview" | "code">(md ? "preview" : "code");
  const [wrap, setWrap] = useState(false);
  const [copied, setCopied] = useState(false);
  useEffect(() => setMode(md ? "preview" : "code"), [file.path, md]);

  const language = getLanguage(file.path);
  const lineCount = file.content ? file.content.replace(/\n$/, "").split("\n").length : 0;

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(file.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  const tool = "rounded-md px-2 py-1 text-[11px] font-medium text-muted transition hover:bg-gold/15 hover:text-gold";
  const toolOn = "rounded-md bg-gold/15 px-2 py-1 text-[11px] font-medium text-gold";

  return (
    <div className="flex min-h-0 flex-col gap-3">
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
        {onBack && (
          <button onClick={onBack} className="text-xs font-medium text-gold hover:underline">
            ← Files
          </button>
        )}
        <FileIcon className="h-4 w-4 text-gold" />
        <span className="truncate text-sm font-semibold" title={file.path}>
          {fileName(file.path)}
        </span>
        <span className="rounded-full bg-gold/15 px-2 py-0.5 text-[10px] font-semibold uppercase text-gold">{language}</span>
        <span className="text-[11px] text-muted">
          {lineCount ? `${lineCount} lines · ` : ""}
          {formatBytes(file.size)}
        </span>
        <div className="ml-auto flex items-center gap-1">
          {md && (
            <>
              <button className={mode === "preview" ? toolOn : tool} onClick={() => setMode("preview")}>
                Preview
              </button>
              <button className={mode === "code" ? toolOn : tool} onClick={() => setMode("code")}>
                Code
              </button>
            </>
          )}
          {!file.is_binary && mode === "code" && (
            <button className={wrap ? toolOn : tool} onClick={() => setWrap((w) => !w)}>
              Wrap
            </button>
          )}
          {!file.is_binary && (
            <button className={tool} onClick={copy}>
              {copied ? "Copied ✓" : "Copy"}
            </button>
          )}
{file.web_url && (
            <a className={tool} href={file.web_url} target="_blank" rel="noreferrer">
              Open on web ↗
            </a>
          )}
          {onExpand && (
            <button className={tool} onClick={onExpand} title="Open large view">
              Expand
            </button>
          )}
          {onClose && (
            <button className={tool} onClick={onClose}>
              Close ✕
            </button>
          )}
        </div>
      </div>

      {file.truncated && <p className="rounded-lg bg-warn/10 px-3 py-1.5 text-xs text-warn">File is large; showing the first 1 MB.</p>}

      <div className={`min-h-0 overflow-auto ${expanded ? "max-h-[75vh]" : "max-h-[26rem]"}`}>
        {file.image_data_url ? (
          <div className="grid place-items-center rounded-xl border border-gold/30 bg-subtle p-4">
            <img src={file.image_data_url} alt={file.path} className="max-h-[70vh] max-w-full rounded-lg" />
          </div>
        ) : file.is_binary ? (
          <EmptyState icon={<FileIcon className="h-6 w-6" />} title="Binary file" hint="This file type can't be previewed. Use the GitHub link to download it." />
        ) : mode === "preview" && md ? (
          <div className="rounded-xl border border-gold/30 bg-subtle p-4">
            <Markdown>{file.content}</Markdown>
          </div>
        ) : file.content === "" ? (
          <EmptyState title="Empty file" />
        ) : (
          <CodeView code={file.content} language={language} wrap={wrap} />
        )}
      </div>
    </div>
  );
}
