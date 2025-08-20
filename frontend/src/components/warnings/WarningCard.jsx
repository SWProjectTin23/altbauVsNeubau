import React from "react";

export default function WarningCard({ metric, values, levelLabels, onChange }) {
  return (
    <div className="warning-card">
      <h3>{metric}</h3>
      {Object.keys(levelLabels).map((level) => (
        <div key={level} className="warning-input-row">
          <label htmlFor={`${metric}-${level}`}>{levelLabels[level]}</label>
          <input
            id={`${metric}-${level}`}
            type="number"
            value={values[level] ?? ""}
            onChange={e => onChange(metric, level, e.target.value)}
          />
        </div>
      ))}
    </div>
  );
}