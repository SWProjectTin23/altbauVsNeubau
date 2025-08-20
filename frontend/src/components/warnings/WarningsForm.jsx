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
  backError
}) {
  return (
    <form className="warnings-grid">
      {Object.entries(warnings).map(([metric, levels]) => (
        <WarningCard
          key={metric}
          metric={metric}
          values={levels}
          levelLabels={levelLabels}
          onChange={handleChange}
        />
      ))}
      <div className="button-group">
        <button
          type="button"
          className="btn"
          onClick={saveThresholds}
          disabled={!isDirty() || saving}
          aria-busy={saving ? "true" : "false"}
        >
          {saving ? "Speichern..." : "Speichern"}
        </button>
        <button type="button" className="btn" onClick={handleBack}>
          Zurück zum Dashboard
        </button>
      </div>
      <ErrorMessage message={saveError} />
      <ErrorMessage message={backError} />
    </form>
  );
}