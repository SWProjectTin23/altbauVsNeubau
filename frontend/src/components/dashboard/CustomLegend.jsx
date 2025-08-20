import React from "react";

export default function CustomLegend({ visibleLines, handleLegendClick }) {
  const legendItems = [
    { value: "Altbau", color: "#e2001a" },
    { value: "Neubau", color: "#434343ff" },
  ];
  return (
    <div className="custom-legend">
      {legendItems.map((entry) => {
        const isActive = visibleLines[entry.value];
        return (
          <span
            key={entry.value}
            onClick={() => handleLegendClick({ dataKey: entry.value })}
            style={{
              marginRight: 16,
              cursor: "pointer",
              color: isActive ? entry.color : "#bbb",
              textDecoration: isActive ? "none" : "line-through",
              opacity: isActive ? 1 : 0.5,
              fontWeight: isActive ? "bold" : "normal",
              userSelect: "none"
            }}
          >
            <svg width="14" height="14" style={{ marginRight: 4, verticalAlign: "middle" }}>
              <rect
                width="14"
                height="14"
                fill={isActive ? entry.color : "#eee"}
                stroke={isActive ? entry.color : "#bbb"}
                strokeWidth="2"
              />
            </svg>
            {entry.value}
          </span>
        );
      })}
    </div>
  );
}