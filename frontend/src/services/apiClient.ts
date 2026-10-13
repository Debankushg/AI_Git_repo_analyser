export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

/** FastAPI errors look like {"detail": "..."}; surface just the readable part. */
async function readError(res: Response): Promise<string> {
  const text = await res.text();
  try {
    const body = JSON.parse(text);
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) return body.detail.map((d: { msg: string }) => d.msg).join(", ");
  } catch {
    /* not JSON */
  }
  return text || res.statusText;
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  } catch {
    throw new ApiError("Failed to fetch", 0);
  }
  if (!res.ok) throw new ApiError(await readError(res), res.status);
  return res.json() as Promise<T>;
}
