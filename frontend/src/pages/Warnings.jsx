import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import './Warnings.css';

const levelLabels = {
  redLow: "Warnwert niedrig rot",
  yellowLow: "Warnwert niedrig gelb",
  yellowHigh: "Warnwert hoch gelb",
  redHigh: "Warnwert hoch rot",
};

const API_BASE = "http://localhost:5001/api";

export default function Warnings() {
  const [warnings, setWarnings] = useState(null);
  const [originalWarnings, setOriginalWarnings] = useState(null); 
  const [loading, setLoading] = useState(true);
  const [saveError, setSaveError] = useState(null);
  const [backError, setBackError] = useState(null);
  const navigate = useNavigate();

  const mapApiToUi = (data) => ({
  Temperatur: {
    redLow: data.temperature_min_soft,
    yellowLow: data.temperature_min_hard,
    yellowHigh: data.temperature_max_soft,
    redHigh: data.temperature_max_hard,
  },
  Luftfeuchtigkeit: {
    redLow: data.humidity_min_soft,
    yellowLow: data.humidity_min_hard,
    yellowHigh: data.humidity_max_soft,
    redHigh: data.humidity_max_hard,
  },
  Pollen: {
    redLow: data.pollen_min_soft,
    yellowLow: data.pollen_min_hard,
    yellowHigh: data.pollen_max_soft,
    redHigh: data.pollen_max_hard,
  },
  Feinpartikel: {
    redLow: data.particulate_matter_min_soft,
    yellowLow: data.particulate_matter_min_hard,
    yellowHigh: data.particulate_matter_max_soft,
    redHigh: data.particulate_matter_max_hard,
  },
});

const mapUiToApi = (uiData) => ({
  temperature_min_soft: uiData.Temperatur.redLow,
  temperature_min_hard: uiData.Temperatur.yellowLow,
  temperature_max_soft: uiData.Temperatur.yellowHigh,
  temperature_max_hard: uiData.Temperatur.redHigh,

  humidity_min_soft: uiData.Luftfeuchtigkeit.redLow,
  humidity_min_hard: uiData.Luftfeuchtigkeit.yellowLow,
  humidity_max_soft: uiData.Luftfeuchtigkeit.yellowHigh,
  humidity_max_hard: uiData.Luftfeuchtigkeit.redHigh,

  pollen_min_soft: uiData.Pollen.redLow,
  pollen_min_hard: uiData.Pollen.yellowLow,
  pollen_max_soft: uiData.Pollen.yellowHigh,
  pollen_max_hard: uiData.Pollen.redHigh,

  particulate_matter_min_soft: uiData.Feinpartikel.redLow,
  particulate_matter_min_hard: uiData.Feinpartikel.yellowLow,
  particulate_matter_max_soft: uiData.Feinpartikel.yellowHigh,
  particulate_matter_max_hard: uiData.Feinpartikel.redHigh,
});

  useEffect(() => {
    const fetchThresholds = async () => {
      try {
        const response = await fetch(`${API_BASE}/thresholds`);
        const result = await response.json();
        if (
          result.status === "success" &&
          Array.isArray(result.data) &&
          result.data.length > 0
        ) {
          const mapped = mapApiToUi(result.data[0]);
          setWarnings(mapped);
          setOriginalWarnings(mapped); // Originalwerte speichern
        } else {
          setSaveError("Warnwerte konnten nicht geladen werden.");
        }
      } catch (error) {
        console.error("Fehler beim Laden:", error);
        setSaveError("Fehler beim Abrufen der Warnwerte.");
      } finally {
        setLoading(false);
      }
    };

    fetchThresholds();
  }, []);

  const isDirty = () => {
    return JSON.stringify(warnings) !== JSON.stringify(originalWarnings);
  };

  const validateWarnings = (warnings) => {
  for (const [metric, levels] of Object.entries(warnings)) {
    if (levels.redLow >= levels.yellowLow) {
      return `Bei "${metric}": "Warnwert niedrig rot" darf nicht größer als "Warnwert niedrig gelb" sein.`;
    }
    if (levels.redLow >= levels.redHigh) {
      return `Bei "${metric}": "Warnwert niedrig rot" muss kleiner als "Warnwert hoch rot" sein.`;
    }
    if (levels.yellowLow >= levels.yellowHigh) {
      return `Bei "${metric}": "Warnwert niedrig gelb" muss kleiner als "Warnwert hoch gelb" sein.`;
    }
  }
  return null;
};

  const handleChange = (metric, level, value) => {
    setWarnings((prev) => ({
      ...prev,
      [metric]: {
        ...prev[metric],
        [level]: Number(value),
      },
    }));
  };

  const handleBack = () => {
    setBackError(null);
    if (isDirty()) {
      setBackError("Es gibt ungespeicherte Änderungen. Bitte speichern oder Änderungen verwerfen.");
    } else {
      navigate("/");
    }
  };

  const saveThresholds = async () => {
    setSaveError(null);
    setBackError(null);

    const validationError = validateWarnings(warnings);
    if (validationError) {
      setSaveError(validationError);
      return;
    }

    try {
      const payload = mapUiToApi(warnings);
      const response = await fetch(`${API_BASE}/thresholds`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (result.status === "success") {
        setOriginalWarnings(warnings); 
        navigate("/");
      } else {
        setSaveError(result.message || "Fehler beim Speichern der Warnwerte.");
        console.error("Fehler beim Speichern:", result);
      }
    } catch (error) {
      console.error("Fehler beim Speichern:", error);
      setSaveError("Ein Fehler ist beim Speichern aufgetreten.");
    }
  };

  if (loading || !warnings) {
    return <div className="warnings-wrapper"><p>Lade Warnwerte...</p></div>;
  }

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
                    <label htmlFor={`${metric}-${level}`} className="input-label">
                      {levelLabels[level] || level}
                    </label>
                    <input
                      id={`${metric}-${level}`}
                      type="number"
                      className="input-field"
                      value={value}
                      onChange={(e) =>
                        handleChange(metric, level, e.target.value)
                      }
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}
          <div className="button-group">
            <button type="button" className="btn" onClick={saveThresholds}>
              Speichern
            </button>
            <button type="button" className="btn" onClick={handleBack}>
              Zurück zum Dashboard
            </button>
          </div>
        </form>
        {saveError && (
        <div className="save-error" style={{ marginTop: 16 }}>
            {saveError}
          </div>
        )}
        {backError && (
        <div className="save-error" style={{ marginTop: 16 }}>
            {backError}
          </div>
        )}
      </div>
    </div>
  );
}
