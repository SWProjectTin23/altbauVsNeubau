import React from "react";

export default function LoadingIndicator({ text = "Lade Warnwerte..." }) {
  return (
    <div className="loading-indicator">
      <p>{text}</p>
    </div>
  );
}