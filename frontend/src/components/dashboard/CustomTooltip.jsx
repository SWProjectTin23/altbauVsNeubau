import React from "react";
import { formatCurrentTimestamp } from "./dashboardUtils";

export default function CustomTooltip({ active, payload, label, unit, metric }) {
  if (active && payload && payload.length) {
    const dateLabel = formatCurrentTimestamp(label);

    return (
      <div className="custom-tooltip" style={{ background: "#fff", border: "1px solid #ccc", padding: "0.5rem" }}>
        <div><strong>{dateLabel}</strong></div>
        {payload.map((entry, idx) => (
          <div key={idx} style={{ color: entry.color }}>
            {entry.name}: {
              typeof entry.value === "number"
                ? (metric === "Temperatur" || metric === "Luftfeuchtigkeit"
                    ? entry.value.toFixed(2)
                    : Math.round(entry.value))
                : "Keine Daten"
            } {typeof entry.value === "number" ? unit : ""}
          </div>
        ))}
      </div>
    );
  }
  return null;
}