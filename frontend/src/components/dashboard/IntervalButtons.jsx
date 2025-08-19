import React from "react";

const intervalLabels = {
  "30min": "30 Minuten",
  "1h": "1 Stunde",
  "3h": "3 Stunden",
  "6h": "6 Stunden",
  "12h": "12 Stunden",
  "1d": "1 Tag",
  "1w": "1 Woche",
  "1m": "1 Monat"
};

export default function IntervalButtons({ intervals, selectedInterval, setSelectedInterval }) {
  return (
    <div className="interval-buttons">
      {intervals.map((key) => (
        <button
          key={key}
          className={`interval-btn ${selectedInterval === key ? "active" : ""}`}
          onClick={() => setSelectedInterval(key)}
        >
          {intervalLabels[key] || key}
        </button>
      ))}
    </div>
  );
}