import React from "react";
import NumberInputWithButtons from "./NumberInputWithButtons";

const integerMetrics = ["Pollen", "Feinstaub"];

export default function WarningCard({ metric, values, levelLabels, onChange }) {
  const isInteger = integerMetrics.includes(metric);

  return (
    <div className="card">
      <div className="warning-title">{metric}</div>
      <div className="warning-inputs">
        {Object.keys(levelLabels).map((level) => (
          <div key={level} className="input-block">
            <label className="input-label" htmlFor={`${metric}-${level}`}>
              {levelLabels[level]}
            </label>
            <NumberInputWithButtons
              value={values[level] ?? ""}
              onChange={val => onChange(metric, level, isInteger ? Math.round(val) : val)}
              min={0}
              step={isInteger ? 1 : 0.1}
              id={`${metric}-${level}`}
            />
          </div>
        ))}
      </div>
    </div>
  );
}