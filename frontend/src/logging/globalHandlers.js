import { feLogger } from "./logger";

// Global error handlers
if (typeof window !== "undefined") {
  window.addEventListener("error", (ev) => {
    feLogger.error("ui", "window.onerror", {
      message: ev.message,
      filename: ev.filename,
      lineno: ev.lineno,
      colno: ev.colno,
      error: ev.error?.stack || String(ev.error),
    });
  });

  // Handle unhandled promise rejections
  window.addEventListener("unhandledrejection", (ev) => {
    feLogger.error("ui", "unhandledrejection", {
      reason: ev.reason && (ev.reason.stack || ev.reason.message || String(ev.reason)),
    });
  });
}