export interface Repository {
  full_name: string;
  description: string | null;
  private: boolean;
}
export interface ContentEntry {
  name: string;
  path: string;
  type: "file" | "dir";
}
export interface RepoFile {
  path: string;
  content: string;
  size: number;
  is_binary: boolean;
  truncated: boolean;
  image_data_url: string | null;
  web_url: string | null;
}
export interface Commit {
  sha: string;
  message: string;
  author_name: string;
  author_login: string | null;
  avatar_url: string | null;
  date: string | null;
  html_url: string | null;
}
export interface PullRequest {
  number: number;
  title: string;
  draft?: boolean;
  html_url?: string;
  user?: { login: string; avatar_url?: string };
  created_at?: string | null;
}
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
export interface PendingAction {
  id: string;
  tool: string;
  arguments: Record<string, unknown>;
  summary: string;
  status: "pending" | "approved" | "rejected";
  result?: string | null;
}
export interface ChatResponse {
  reply: string;
  tool_calls: string[];
  pending_actions: PendingAction[];
}
export interface ApiEndpoint {
  method: string;
  path: string;
  category: string;
  summary: string;
}
export interface EndpointCatalog {
  total: number;
  endpoints: ApiEndpoint[];
}
export interface RepositoryDetail {
  id: string; // use this in every API call
  provider: "github" | "gitlab" | "git";
  supports_pull_requests: boolean;
  pull_request_label: string;
  full_name: string;
  description: string | null;
  private: boolean;
  default_branch: string | null;
  language: string | null;
  stars: number;
  forks: number;
  open_issues: number;
  html_url: string | null;
  owner_avatar_url: string | null;
}
export interface LinkTarget {
  kind: "repo" | "tree" | "blob" | "pull" | "issue" | "commit";
  ref: string | null;
  path: string;
  number: number | null;
  sha: string | null;
}
export interface ResolveResponse {
  repository: RepositoryDetail;
  target: LinkTarget;
}
