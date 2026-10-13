export type ErrorKind = "rate-limit" | "network" | "not-found" | "server";

export interface ErrorInfo {
  kind: ErrorKind;
  title: string;
  message: string;
}

/** Turn a raw error message into a friendly title + explanation. */
export function describeError(raw: string): ErrorInfo {
  const m = raw.toLowerCase();
  if (m.includes("rate limit") || m.includes("429") || m.includes("quota"))
    return { kind: "rate-limit", title: "Rate limit reached", message: raw.length < 160 ? raw : "The AI service is receiving too many requests. Wait a minute and try again." };
  if (m.includes("failed to fetch") || m.includes("networkerror") || m.includes("econnrefused"))
    return { kind: "network", title: "Can't reach the server", message: "Check that the backend is running on port 8000, then retry." };
  if (m.includes("404") || m.includes("not found"))
    return { kind: "not-found", title: "Not found", message: raw };
  return { kind: "server", title: "Something went wrong", message: raw || "Unexpected error. Please try again." };
}
