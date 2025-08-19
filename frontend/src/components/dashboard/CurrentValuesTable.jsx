import React from "react";
import { getWarningClass, formatCurrentTimestamp } from "./dashboardUtils";

const metricUnits = {
  Temperatur: "°C",
  Luftfeuchtigkeit: "%",
  Pollen: "µg/m³",
  Feinstaub: "µg/m³",
};

export default function CurrentValuesTable({ metrics, currentData, warningThresholds }) {
  return (
    <div className="table-wrapper">
      <table className="metrics-table">
        <thead>
          <tr>
            <th>Metrik</th>
            <th>Altbau</th>
            <th>Neubau</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((metric) => (
            <tr key={metric}>
              <td>{metric}</td>
              <td className={getWarningClass(warningThresholds, metric, currentData.Altbau?.[metric])}>
                {currentData.Altbau
                  ? (currentData.Altbau[metric] ?? "—") + (currentData.Altbau[metric] ? ` ${metricUnits[metric]}` : "")
                  : <span className="chart-error">Sensor nicht verfügbar</span>
                }
              </td>
              <td className={getWarningClass(warningThresholds, metric, currentData.Neubau?.[metric])}>
                {currentData.Neubau
                  ? (currentData.Neubau[metric] ?? "—") + (currentData.Neubau[metric] ? ` ${metricUnits[metric]}` : "")
                  : <span className="chart-error">Sensor nicht verfügbar</span>
                }
              </td>
            </tr>
          ))}
          <tr>
            <td style={{ fontWeight: "bold", color: "#555" }}>Zeitstempel</td>
            <td style={{ color: "#555" }}>
              {currentData.Altbau && currentData.Altbau.timestamp
                ? formatCurrentTimestamp(currentData.Altbau.timestamp)
                : currentData.Altbau
                  ? "—"
                  : <span className="chart-error">Sensor nicht verfügbar</span>
              }
            </td>
            <td style={{ color: "#555" }}>
              {currentData.Neubau && currentData.Neubau.timestamp
                ? formatCurrentTimestamp(currentData.Neubau.timestamp)
                : currentData.Neubau
                  ? "—"
                  : <span className="chart-error">Sensor nicht verfügbar</span>
              }
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}