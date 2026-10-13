import type { Commit, ContentEntry, EndpointCatalog, PullRequest, RepoFile, Repository, RepositoryDetail, ResolveResponse } from "../types";
import { api } from "./apiClient";

const q = (params: Record<string, string | number | null | undefined>) =>
  Object.entries(params)
    .filter(([, v]) => v !== null && v !== undefined && v !== "")
    .map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`)
    .join("&");

// `repo` is the repository id returned by resolve: "owner/name" (GitHub) or "host/group/name" (any other git host).
export const getRepositories = () => api<Repository[]>("/repositories");
export const resolveRepositoryLink = (url: string) =>
  api<ResolveResponse>("/repositories/resolve", { method: "POST", body: JSON.stringify({ url }) });
export const getRepositoryDetail = (repo: string) => api<RepositoryDetail>(`/repositories/detail?${q({ repo })}`);
export const getContents = (repo: string, path = "", ref?: string | null) =>
  api<ContentEntry[]>(`/repositories/contents?${q({ repo, path, ref })}`);
export const getFile = (repo: string, path: string, ref?: string | null) => api<RepoFile>(`/repositories/file?${q({ repo, path, ref })}`);
export const getCommits = (repo: string, limit = 30) => api<Commit[]>(`/repositories/commits?${q({ repo, limit })}`);
export const getPulls = (repo: string) => api<PullRequest[]>(`/repositories/pulls?${q({ repo })}`);
export const getEndpoints = () => api<EndpointCatalog>("/meta/endpoints");
