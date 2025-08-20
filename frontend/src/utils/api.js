import { feLogger } from "../logging/logger";
import { ApiError, NetworkError } from "../errors";

// Determine API base URL at runtime
const RUNTIME_API =
  typeof window !== "undefined" && window.__APP_CONFIG__ && window.__APP_CONFIG__.API_BASE;

// Determine API base URL at build time
const ENV_API =
  process.env.REACT_APP_API_URL || process.env.VITE_API_URL || process.env.REACT_APP_API_BASE;

// Determine API base URL to use
const API_BASE = RUNTIME_API || ENV_API || "/api";

function buildUrl(path) {
  // If path is already a full URL, use it directly
  if (path.startsWith("http")) return path;
  // Otherwise, append to the base URL (without double slash)
  return `${API_BASE.replace(/\/$/, "")}${path.startsWith("/") ? path : "/" + path}`;
}

async function request(method, path, body) {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const init = {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  };

  try {
    const res = await fetch(url, init);
    const isJson = res.headers.get("content-type")?.includes("application/json");
    const data = isJson ? await res.json() : await res.text();

    if (!res.ok || (isJson && data && data.status === "error")) {
      const message =
        (isJson && data && (data.message || data.error)) ||
        `HTTP ${res.status} ${res.statusText}`;
      feLogger.warn("api", "response-error", { url, status: res.status, body: data });
      throw new ApiError(message, res.status, data, { url, method });
    }

    feLogger.debug("api", "response-ok", { url, status: res.status });
    return data;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    feLogger.error("api", "network-error", { url, error: String(err) });
    throw new NetworkError("Netzwerkfehler – bitte später erneut versuchen.", { url, method });
  }
}

export const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
};