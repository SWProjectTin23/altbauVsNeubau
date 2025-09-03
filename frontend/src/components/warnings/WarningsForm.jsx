import React from "react";
import WarningCard from "./WarningCard";
import ErrorMessage from "./ErrorMessage";

export default function WarningsForm({
  warnings,
  levelLabels,
  handleChange,
  saveThresholds,
  isDirty,
  saving,
  handleBack,
  saveError,
  backError,
  infoMessage,
  alertEmail,
  setAlertEmail
}) {
  return (
    <form className="warnings-form">
      <div className="email-field">
        <label htmlFor="alertEmail">Alert-Mail-Adresse:</label>
        <input
          type="email"
          id="alertEmail"
          value={alertEmail}
          onChange={e => setAlertEmail(e.target.value)}
          placeholder="E-Mail für Alerts"
          required
        />
      </div>
      <div className="grid-2">
        {Object.entries(warnings).map(([metric, levels]) => (
          <WarningCard
            key={metric}
            metric={metric}
            values={levels}
            levelLabels={levelLabels}
            onChange={handleChange}
          />
        ))}
      </div>
      <ErrorMessage message={saveError} />
      <ErrorMessage message={backError} />
      {infoMessage && (
        <div className="info-message">
          <span className="icon">ℹ️</span>
          {infoMessage}
        </div>
      )}
      <div className="button-group">
        <button
          type="button"
          className="btn"
          onClick={saveThresholds}
          disabled={!isDirty() || saving}
          aria-busy={saving ? { opacity: 0.7, pointerEvents: "none" } : {}}
        >
          {saving ? (
            <>
              <span className="spinner" style={{
                display: "inline-block",
                width: 16,
                height: 16,
                border: "2px solid #ccc",
                borderTop: "2px solid #e2001a",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
                marginRight: 8
              }} />
              Speichern...
            </>
          ) : "Speichern"}
        </button>
        <button type="button" className="btn" onClick={handleBack}>
          Zurück zum Dashboard
        </button>
      </div>
    </form>
  );
}