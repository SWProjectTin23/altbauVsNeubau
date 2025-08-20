const LEVELS = ["debug", "info", "warn", "error"];

const envLevel =
  (import.meta && import.meta.env && import.meta.env.VITE_LOG_LEVEL) ||
  process.env.REACT_APP_LOG_LEVEL ||
  "info";

const minLevelIndex = Math.max(0, LEVELS.indexOf((envLevel || "info").toLowerCase()));

function shouldLog(level) {
  return LEVELS.indexOf(level) >= minLevelIndex;
}

// Optional: Logs an einen Backend-Endpunkt senden (per ENV konfigurierbar)
function sendRemote(area, event, level, details) {
  try {
    const endpoint =
      (import.meta.env && import.meta.env.VITE_FE_LOG_ENDPOINT) ||
      process.env.REACT_APP_FE_LOG_ENDPOINT ||
      null;
    if (!endpoint) return;
    const payload = JSON.stringify({
      ts: new Date().toISOString(),
      area,
      event,
      level,
      details,
      ua: typeof navigator !== "undefined" ? navigator.userAgent : undefined,
    });
    if (navigator.sendBeacon) {
      navigator.sendBeacon(endpoint, payload);
    } else {
      fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: payload }).catch(() => {});
    }
  } catch {
    // ignore
  }
}

function log(area, event, level, details) {
  if (!shouldLog(level)) return;
  const msg = `[${level.toUpperCase()}] [${area}] ${event}`;
  const data = details !== undefined ? details : "";
  if (level === "error") console.error(msg, data);
  else if (level === "warn") console.warn(msg, data);
  else if (level === "info") console.info(msg, data);
  else console.debug(msg, data);
  sendRemote(area, event, level, details);
}

export const feLogger = {
  debug: (area, event, details) => log(area, event, "debug", details),
  info: (area, event, details) => log(area, event, "info", details),
  warn: (area, event, details) => log(area, event, "warn", details),
  error: (area, event, details) => log(area, event, "error", details),
};