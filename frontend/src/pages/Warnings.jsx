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
  const [alertEmail, setAlertEmail] = useState("");
  const [originalAlertEmail, setOriginalAlertEmail] = useState("");

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
    const fetchAlertEmail = async () => {
      try {
        const result = await api.get("/alert_email");
        if (result.status === "success") {
          setAlertEmail(result.email);
          setOriginalAlertEmail(result.email);
        }
      } catch (error) {
        feLogger.error("warnings", "fetch-alert-email-failed", { error: String(error) });
      }
    };
    fetchThresholds();
    fetchAlertEmail();
  }, []);

  // Check if the form is dirty (i.e., has unsaved changes)
  const isDirty = () => {
    return (
      JSON.stringify(warnings) !== JSON.stringify(originalWarnings) ||
      saveError !== null ||
      alertEmail !== (originalAlertEmail ?? "")
    );
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

  const validateEmail = (email) => {
    if (!email) return "Bitte eine E-Mail-Adresse eingeben.";
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!re.test(email)) return "Bitte eine gültige E-Mail-Adresse eingeben.";
    return null;
  };

  // Save the warning thresholds
  const saveThresholds = async () => {
  setSaveError(null);
  setBackError(null);

  // Validate thresholds
  const validationError = validateWarnings(warnings);
  if (validationError) {
    setSaveError(validationError);
    return;
  }

  // Validate email
  const emailError = validateEmail(alertEmail);
  if (emailError) {
    setSaveError(emailError);
    return;
  }

  setSaving(true);

  try {
    // 1. Speichere die E-Mail
    const emailResult = await api.post("/alert_email", { alert_email: alertEmail });
    if (emailResult.status !== "success") {
      setSaveError(emailResult.message || "Fehler beim Speichern der Alert-Mail-Adresse.");
      setSaving(false);
      return;
    }

    // 2. Speichere die Warnwerte
    const payload = { ...mapUiToApi(warnings), alert_email: alertEmail };
    const result = await api.post("/thresholds", payload);
    if (result.status === "success") {
      setOriginalWarnings(warnings);
      setTimeout(() => navigate("/"), 1200); // Optional: Erfolg anzeigen, dann weiterleiten
    } else {
      setSaveError(result.message || "Fehler beim Speichern der Warnwerte.");
    }
  } catch (error) {
    setSaveError("Ein Fehler ist beim Speichern aufgetreten.");
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
          alertEmail={alertEmail}
          setAlertEmail={setAlertEmail}
        />
      </div>
    </div>
  );
}
