import { feLogger } from "../logging/logger";
import { ApiError, NetworkError } from "../errors";

const RUNTIME_API =
  typeof window !== "undefined" && window.__APP_CONFIG__ && window.__APP_CONFIG__.API_BASE;


const API_BASE =
  RUNTIME_API ||
  process.env.REACT_APP_API_BASE ||   
  "/api";    

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