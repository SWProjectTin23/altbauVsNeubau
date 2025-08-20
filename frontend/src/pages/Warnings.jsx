import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import './Warnings.css';
import { api } from "../utils/api";              
import { feLogger } from "../logging/logger"; 
import { mapApiToUi, mapUiToApi, validateWarnings } from "../components/warnings/warningsUtils";
import LoadingIndicator from "../components/warnings/LoadingIndicator";
import ErrorMessage from "../components/warnings/ErrorMessage";
import WarningsForm from "../components/warnings/WarningsForm";

// Define the warning level labels
const levelLabels = {
  redLow: "Warnwert niedrig rot",
  yellowLow: "Warnwert niedrig gelb",
  yellowHigh: "Warnwert hoch gelb",
  redHigh: "Warnwert hoch rot",
};

// Warnings component
export default function () {
  const [warnings, setWarnings] = useState(null);
  const [originalWarnings, setOriginalWarnings] = useState(null); 
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [backError, setBackError] = useState(null);
  const navigate = useNavigate();

  // Fetch initial data
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

  // Check if the form is dirty (i.e., has unsaved changes)
  const isDirty = () => {
    return JSON.stringify(warnings) !== JSON.stringify(originalWarnings);
  };

  // Handle changes to the warning thresholds
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

  // Handle back navigation
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

  // Save the warning thresholds
  const saveThresholds = async () => {
    setSaveError(null);
    setBackError(null);

    // Validate the warning thresholds
    const validationError = validateWarnings(warnings);
    if (validationError) {
      setSaveError(validationError);
      feLogger.warn("warnings", "validation-failed", { validationError, warnings });
      return;
    }

    setSaving(true);
    feLogger.info("warnings", "save-start", {});

    // Map the UI format to API format
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

  // Loading state
  if (loading || !warnings) {
    return (
      <div className="warnings-wrapper">
        <LoadingIndicator text="Lade Warnwerte..." />
      </div>
    );
  }

  // Render the warning thresholds form
  return (
    <div className="warnings-wrapper">
      <div className="warnings-container">
        <h1 className="section-title">Warnwerte anpassen</h1>
        <WarningsForm
          warnings={warnings}
          levelLabels={levelLabels}
          handleChange={handleChange}
          saveThresholds={saveThresholds}
          isDirty={isDirty}
          saving={saving}
          handleBack={handleBack}
          saveError={saveError}
          backError={backError}
        />
      </div>
    </div>
  );
}
