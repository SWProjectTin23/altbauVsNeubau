import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import './Warnings.css'

const levelLabels = {
  redLow: "Warnwert niedrig rot",
  yellowLow: "Warnwert niedrig gelb",
  yellowHigh: "Warnwert hoch gelb",
  redHigh: "Warnwert hoch Rot",
};

export default function Warnings() {
  const [warnings, setWarnings] = useState({
    Temperatur: { redLow: 15, yellowLow: 18, yellowHigh: 25, redHigh: 30 },
    Luftfeuchtigkeit: { redLow: 30, yellowLow: 40, yellowHigh: 60, redHigh: 70 },
    Pollen: { redLow: 0, yellowLow: 30, yellowHigh: 100, redHigh: 150 },
    Feinpartikel: { redLow: 0, yellowLow: 10, yellowHigh: 20, redHigh: 30 },
  });

  const navigate = useNavigate();

  const handleChange = (metric, level, value) => {
    setWarnings((prev) => ({
      ...prev,
      [metric]: {
        ...prev[metric],
        [level]: Number(value),
      },
    }));
  };

  return (
    <div className="warnings-wrapper">
      <div className="warnings-container">
        <h1 className="section-title">Warnwerte anpassen</h1>
        <form className="warnings-grid">
          {Object.entries(warnings).map(([metric, levels]) => (
            <div key={metric} className="warning-card">
              <h2 className="warning-title">{metric}</h2>
              <div className="warning-inputs">
                {Object.entries(levels).map(([level, value]) => (
                  <div key={level} className="input-block">
                    <label className="input-label">
                      {levelLabels[level] || level}
                    </label>
                    <input
                      type="number"
                      className="input-field"
                      value={value}
                      onChange={(e) => handleChange(metric, level, e.target.value)}
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div className="button-group">
            <button
              type="button"
              className="btn"
              onClick={() => alert("Warnwerte gespeichert (Demo-Modus)")}
            >
              Speichern
            </button>
            <button
              onClick={() => navigate("/")}
              className="btn"
            >
              Zurück zum Dashboard
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
