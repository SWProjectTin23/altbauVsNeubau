import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import './Warnings.css';
import { api } from "../utils/api";              
import { feLogger } from "../logging/logger"; 

const levelLabels = {
  redLow: "Warnwert niedrig rot",
  yellowLow: "Warnwert niedrig gelb",
  yellowHigh: "Warnwert hoch gelb",
  redHigh: "Warnwert hoch rot",
};

export default function Warnings() {
  const [warnings, setWarnings] = useState(null);
  const [originalWarnings, setOriginalWarnings] = useState(null); 
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [backError, setBackError] = useState(null);
  const navigate = useNavigate();

  const mapApiToUi = (data) => ({
  Temperatur: {
    redLow: data.temperature_min_hard,    // min_hard = rot
    yellowLow: data.temperature_min_soft, // min_soft = gelb
    yellowHigh: data.temperature_max_soft,// max_soft = gelb
    redHigh: data.temperature_max_hard,   // max_hard = rot
  },
  Luftfeuchtigkeit: {
    redLow: data.humidity_min_hard,
    yellowLow: data.humidity_min_soft,
    yellowHigh: data.humidity_max_soft,
    redHigh: data.humidity_max_hard,
  },
  Pollen: {
    redLow: data.pollen_min_hard,
    yellowLow: data.pollen_min_soft,
    yellowHigh: data.pollen_max_soft,
    redHigh: data.pollen_max_hard,
  },
  Feinpartikel: {
    redLow: data.particulate_matter_min_hard,
    yellowLow: data.particulate_matter_min_soft,
    yellowHigh: data.particulate_matter_max_soft,
    redHigh: data.particulate_matter_max_hard,
  },
});

const mapUiToApi = (uiData) => ({
  temperature_min_hard: uiData.Temperatur.redLow,
  temperature_min_soft: uiData.Temperatur.yellowLow,
  temperature_max_soft: uiData.Temperatur.yellowHigh,
  temperature_max_hard: uiData.Temperatur.redHigh,

  humidity_min_hard: uiData.Luftfeuchtigkeit.redLow,
  humidity_min_soft: uiData.Luftfeuchtigkeit.yellowLow,
  humidity_max_soft: uiData.Luftfeuchtigkeit.yellowHigh,
  humidity_max_hard: uiData.Luftfeuchtigkeit.redHigh,

  pollen_min_hard: uiData.Pollen.redLow,
  pollen_min_soft: uiData.Pollen.yellowLow,
  pollen_max_soft: uiData.Pollen.yellowHigh,
  pollen_max_hard: uiData.Pollen.redHigh,

  particulate_matter_min_hard: uiData.Feinpartikel.redLow,
  particulate_matter_min_soft: uiData.Feinpartikel.yellowLow,
  particulate_matter_max_soft: uiData.Feinpartikel.yellowHigh,
  particulate_matter_max_hard: uiData.Feinpartikel.redHigh,
});

  useEffect(() => {
    const fetchThresholds = async () => {
      feLogger.info("warnings", "fetch-start", {});
      try {
        const result = await api.get("/thresholds");
        if (
          result.status === "success" &&
          Array.isArray(result.data) &&
          result.data.length > 0
        ) {
          const mapped = mapApiToUi(result.data[0]);
          setWarnings(mapped);
          setOriginalWarnings(mapped);
          feLogger.info("warnings", "fetch-success", { count: result.data.length });
        } else {
          setSaveError("Warnwerte konnten nicht geladen werden.");
          feLogger.warn("warnings", "fetch-empty", { result });
        }
      } catch (error) {
        setSaveError("Fehler beim Abrufen der Warnwerte.");
        feLogger.error("warnings", "fetch-failed", { error: String(error) });
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
    setWarnings((prev) => {
      const next = {
        ...prev,
        [metric]: { ...prev[metric], [level]: Number(value) },
      };
      feLogger.debug("warnings", "field-change", { metric, level, value: Number(value) });
      return next;
    });
  };

  const handleBack = () => {
    setBackError(null);
    if (isDirty()) {
      setBackError("Es gibt ungespeicherte Änderungen. Bitte speichern oder Änderungen verwerfen.");
      feLogger.warn("warnings", "back-blocked-unsaved", {});
    } else {
      feLogger.info("warnings", "navigate-back", {});
      navigate("/");
    }
  };

  const saveThresholds = async () => {
    setSaveError(null);
    setBackError(null);

    const validationError = validateWarnings(warnings);
    if (validationError) {
      setSaveError(validationError);
      feLogger.warn("warnings", "validation-failed", { validationError, warnings });
      return;
    }

    setSaving(true);
    feLogger.info("warnings", "save-start", {});


    try {
      const payload = mapUiToApi(warnings);
      const result = await api.post("/thresholds", payload);  
      if (result.status === "success") {
        setOriginalWarnings(warnings);
        feLogger.info("warnings", "save-success", { warnings });
        navigate("/");
      } else {
        const msg = result.message || "Fehler beim Speichern der Warnwerte.";
        setSaveError(msg);
        feLogger.warn("warnings", "save-error", { result });
      }
    } catch (error) {
      setSaveError("Ein Fehler ist beim Speichern aufgetreten.");
      feLogger.error("warnings", "save-failed", { error: String(error) });
    } finally {
      setSaving(false);
    } 
  };

  if (loading || !warnings) {
    return (
      <div className="warnings-wrapper">
        <p>Lade Warnwerte...</p>
      </div>
    );
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
              onClick={saveThresholds}
              disabled={!isDirty() || saving}          // + deaktivieren wenn unverändert/saving
              aria-busy={saving ? "true" : "false"}
            >
              {saving ? "Speichern..." : "Speichern"}
            </button>
            <button type="button" className="btn" onClick={handleBack}>
              Zurück zum Dashboard
            </button>
          </div>
        </form>
        {saveError && <div className="save-error" style={{ marginTop: 16 }}>{saveError}</div>}
        {backError && <div className="save-error" style={{ marginTop: 16 }}>{backError}</div>}
      </div>
    </div>
  );
}
