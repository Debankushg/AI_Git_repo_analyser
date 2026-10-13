import { useEffect, useRef, useState } from "react";
import AnalysisPanel from "../components/analysis/AnalysisPanel";
import ApprovalModal from "../components/approval/ApprovalModal";
import ChatPanel from "../components/chat/ChatPanel";
import EmptyState from "../components/common/EmptyState";
import { ApiIcon, BugIcon, CommitIcon, FolderIcon, PullIcon, ShieldIcon, SparkIcon } from "../components/common/Icons";
import Panel from "../components/common/Panel";
import RepositoryExplorer, { type ExplorerTarget } from "../components/explorer/RepositoryExplorer";
import CommitList from "../components/issues/CommitList";
import PullRequestList from "../components/issues/PullRequestList";
import EndpointsPanel from "../components/endpoints/EndpointsPanel";
import Header from "../components/layout/Header";
import RepositoryInfoBar from "../components/repository/RepositoryInfoBar";
import RepositoryLinkInput from "../components/repository/RepositoryLinkInput";
import RepositorySelector from "../components/repository/RepositorySelector";
import { useAsync } from "../hooks/useAsync";
import { useChat } from "../hooks/useChat";
import { getRepositoryDetail } from "../services/repositoryService";
import type { Repository, ResolveResponse } from "../types";

export default function DashboardPage() {
  const [repo, setRepo] = useState<string | null>(null);
  const chat = useChat(repo);
  const [tab, setTab] = useState<"commits" | "pulls">("commits");
  const detail = useAsync(() => (repo ? getRepositoryDetail(repo) : Promise.resolve(null)), [repo]);
  const prLabel = detail.data?.pull_request_label ?? "Pull requests";
  const [linked, setLinked] = useState<Repository[]>([]); // repositories opened from a pasted link
  const [target, setTarget] = useState<ExplorerTarget | null>(null);

  // A pasted link: add the repo to the selector, open it, and jump to the file/folder/PR it points to.
  const openFromLink = ({ repository, target: t }: ResolveResponse) => {
    const entry: Repository = { full_name: repository.id, description: repository.description, private: repository.private };
    setLinked((prev) => (prev.some((r) => r.full_name === entry.full_name) ? prev : [entry, ...prev]));
    setRepo(repository.id);
    setTarget({ ...t, nonce: Date.now() });
    if (t.kind === "pull") setTab("pulls");
    else if (t.kind === "commit") setTab("commits");
  };

  const lastReply = [...chat.messages].reverse().find((m) => m.role === "assistant")?.content ?? null;
  const pending = chat.actions.filter((a) => a.status === "pending").length;
  const [approvalsOpen, setApprovalsOpen] = useState(false);
  const prevPending = useRef(0);

  // Open the approval window automatically when the AI proposes a new write action.
  useEffect(() => {
    if (pending > prevPending.current) setApprovalsOpen(true);
    prevPending.current = pending;
  }, [pending]);

  return (
    <div className="flex min-h-screen flex-col lg:h-screen">
      <Header>
        <RepositoryLinkInput onResolved={openFromLink} />
        <RepositorySelector value={repo} extra={linked} onChange={(r) => { setTarget(null); setRepo(r); }} />
        {repo && (
          <button onClick={() => setApprovalsOpen(true)} className="btn-ghost relative h-9 gap-1.5" title="Review actions proposed by the AI">
            <ShieldIcon className="h-4 w-4 text-gold" />
            <span className="hidden sm:inline">Approvals</span>
            {pending > 0 && <span className="grid h-5 min-w-5 animate-pulse place-items-center rounded-full bg-warn px-1 text-[11px] font-bold text-white dark:text-canvas">{pending}</span>}
          </button>
        )}
      </Header>

      {repo && <RepositoryInfoBar detail={detail.data && detail.data.id === repo ? detail.data : null} activeRef={target?.ref} />}

      {!repo ? (
        <main className="grid flex-1 place-items-center p-6">
          <EmptyState
            icon={<SparkIcon className="h-10 w-10 text-gold" />}
            title="Select a repository or paste a git link"
            hint="Paste a repo, folder, file or pull request link from GitHub, GitLab, Bitbucket or any git host. Everything is detected automatically."
          />
        </main>
      ) : (
        <main className="grid min-h-0 min-w-0 flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-12 lg:overflow-hidden">
          <Panel title="Explorer" icon={<FolderIcon />} className="lg:col-span-3">
            <RepositoryExplorer repo={repo} target={target} />
          </Panel>

          <div className="grid min-h-0 min-w-0 gap-4 lg:col-span-6 lg:grid-rows-[3fr_2fr]">
            <Panel title="AI Chat" icon={<SparkIcon />}>
              <ChatPanel messages={chat.messages} loading={chat.loading} error={chat.error} onSend={chat.send} onRetry={chat.retry} onDismissError={chat.dismissError} />
            </Panel>
            <Panel title="AI Analysis" icon={<BugIcon />}>
              <AnalysisPanel lastReply={lastReply} toolCalls={chat.toolCalls} disabled={chat.loading} onRun={chat.send} />
            </Panel>
          </div>

          <div className="grid min-h-0 min-w-0 gap-4 lg:col-span-3 lg:grid-rows-2">
            <Panel title={`Commits & ${detail.data?.provider === "gitlab" ? "MRs" : "PRs"}`} icon={tab === "commits" ? <CommitIcon /> : <PullIcon />}>
              <div className="mb-3 inline-flex rounded-lg bg-subtle p-1 text-xs font-medium">
                {(["commits", "pulls"] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTab(t)}
                    className={`rounded-md px-3 py-1 transition ${tab === t ? "gold-fill text-[#2b1d03] shadow-gold" : "text-muted hover:text-fg"}`}
                  >
                    {t === "commits" ? "Commits" : prLabel}
                  </button>
                ))}
              </div>
              {tab === "commits" ? <CommitList repo={repo} /> : <PullRequestList repo={repo} label={prLabel} supported={detail.data?.supports_pull_requests ?? true} />}
            </Panel>
            <Panel title="API Endpoints" icon={<ApiIcon />}>
              <EndpointsPanel />
            </Panel>
          </div>
        </main>
      )}
      {approvalsOpen && <ApprovalModal actions={chat.actions} onResolve={chat.resolve} onClose={() => setApprovalsOpen(false)} />}
    </div>
  );
}
