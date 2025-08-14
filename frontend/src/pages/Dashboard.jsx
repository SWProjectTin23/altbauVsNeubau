import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import './Dashboard.css';

import { api } from "../utils/api";
import { feLogger } from "../logging/logger";

// Define the metrics and intervals
const metrics = ["Temperatur", "Luftfeuchtigkeit", "Pollen", "Feinstaub"];

const metricUnits = {
  Temperatur: "°C",
  Luftfeuchtigkeit: "%",
  Pollen: "µg/m³",
  Feinstaub: "µg/m³",
};

const intervals = ["30min", "1h", "3h", "6h", "12h", "1d", "1w", "1m"];

// Function to map API data to UI thresholds
const mapApiToUi = (data) => ({
  Temperatur: {
    redLow: data.temperature_min_hard,
    yellowLow: data.temperature_min_soft,
    yellowHigh: data.temperature_max_soft,
    redHigh: data.temperature_max_hard,
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
  Feinstaub: {
    redLow: data.particulate_matter_min_hard,
    yellowLow: data.particulate_matter_min_soft,
    yellowHigh: data.particulate_matter_max_soft,
    redHigh: data.particulate_matter_max_hard,
  },
});

// Function to get the warning class based on thresholds and metric value
const getWarningClass = (thresholds, metric, value) => {
  if (!thresholds || !thresholds[metric]) return "";
  const t = thresholds[metric];
  if (value < t.redLow || value > t.redHigh) return "warn-red";
  if (value < t.yellowLow || value > t.yellowHigh) return "warn-yellow";
  return "";
};

function formatXAxisLabelFromTimestamp(ts) {
  if (!ts) return "";
  const date = new Date(ts * 1000);
  const datum = date.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "2-digit" });
  const zeit = date.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
  const selectedInterval = window.selectedInterval;
  if (selectedInterval === "1w" || selectedInterval === "1m") {
    return `${datum}\n${zeit}`;
  }
  return `${datum}, ${zeit}`;
}

function formatCurrentTimestamp(ts) {
  if (!ts) return "";
  const date = new Date(ts * 1000);
  return date.toLocaleString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function CustomTooltip({ active, payload, label, unit, metric }) {
  if (active && payload && payload.length) {
    const dateLabel = formatCurrentTimestamp(label);

    return (
      <div className="custom-tooltip" style={{ background: "#fff", border: "1px solid #ccc", padding: "0.5rem" }}>
        <div><strong>{dateLabel}</strong></div>
        {payload.map((entry, idx) => (
          <div key={idx} style={{ color: entry.color }}>
            {entry.name}: {
              typeof entry.value === "number"
                ? (metric === "Temperatur" || metric === "Luftfeuchtigkeit"
                    ? entry.value.toFixed(2)
                    : Math.round(entry.value))
                : "Keine Daten"
            } {typeof entry.value === "number" ? unit : ""}
          </div>
        ))}
      </div>
    );
  }
  return null;
}

function getIntervalRange(selectedInterval) {
  const end = Math.floor(Date.now() / 1000);
  let start;
  if (selectedInterval === "30min") start = end - 1800;
  else if (selectedInterval === "1h") start = end - 3600;
  else if (selectedInterval === "3h") start = end - 3 * 3600;
  else if (selectedInterval === "6h") start = end - 6 * 3600;
  else if (selectedInterval === "12h") start = end - 12 * 3600;
  else if (selectedInterval === "1d") start = end - 24 * 3600;
  else if (selectedInterval === "1w") start = end - 7 * 24 * 3600;
  else start = end - 30 * 24 * 3600;
  return { start, end };
}

/**
 * Verarbeitet die Daten eines einzelnen Geräts und fügt bei Zeitlücken null-Punkte ein.
 * @param {Array<Object>} data - Das Daten-Array eines einzelnen Geräts.
 * @param {number} gapSeconds - Die Schwellenwert-Zeitlücke in Sekunden.
 * @returns {Array<Object>} - Das aufbereitete Daten-Array.
 */
function insertGapsInSingleDeviceData(data, gapSeconds) {
  if (!data || data.length === 0) return [];
  const result = [];
  data.forEach((d, i) => {
    if (i > 0) {
      const diff = d.timestamp - data[i - 1].timestamp;
      if (diff > gapSeconds) {
        console.log(`Gap eingefügt bei ${d.timestamp}: Abstand ${diff} Sekunden`);
        result.push({ timestamp: data[i - 1].timestamp + gapSeconds, value: null });
      }
      console.log(`Abstand zwischen ${data[i - 1].timestamp} und ${d.timestamp}: ${diff} Sekunden`);
    }
    result.push({ timestamp: d.timestamp, value: d.value });
  });
  return result;
}

function getMinMax(data, keys, padding = 0.05, metric = "Temperatur") {
  let min = Infinity;
  let max = -Infinity;
  keys.forEach(key => {
    if (data[key]) {
      data[key].forEach(d => {
        if (typeof d.value === "number") {
          if (d.value < min) min = d.value;
          if (d.value > max) max = d.value;
        }
      });
    }
  });

  if (min === Infinity || max === -Infinity) return [0, 1];

  const range = max - min;
  const pad = range > 0 ? range * padding : 1;

  if (metric === "Temperatur" || metric === "Luftfeuchtigkeit") {
    return [
      +(min - pad).toFixed(2),
      +(max + pad).toFixed(2)
    ];
  } else {
    return [
      Math.floor(min - pad),
      Math.ceil(max + pad)
    ];
  }
}

// Haupt-Dashboard-Komponente
export default function Dashboard() {
  const [selectedInterval, setSelectedInterval] = useState("3h");
  const [currentData, setCurrentData] = useState(null);
  const [warningThresholds, setWarningThresholds] = useState(null);
  const [openChart, setOpenChart] = useState(null);
  const [chartData, setChartData] = useState({});
  const [visibleLines, setVisibleLines] = useState({ Altbau: true, Neubau: true });
  const [currentError, setCurrentError] = useState(null);
  const [chartError, setChartError] = useState(null);
  const navigate = useNavigate();

  // Define dynamic gap seconds for line breaks
  const gapMap = {
    "30min": 180,      // 3 Minuten
    "1h": 300,         // 5 Minuten
    "3h": 600,         // 10 Minuten
    "6h": 900,        // 15 Minuten
    "12h": 1800,       // 30 Minuten
    "1d": 3600,        // 1 Stunde
    "1w": 10800,       // 3 Stunden
    "1m": 43200        // 12 Stunden
  };
  const gapSeconds = gapMap[selectedInterval] || 600;

  const timeAsync = async (label, fn) => {
    const t0 = performance.now();
    try {
      return await fn();
    } finally {
      const ms = +(performance.now() - t0).toFixed(0);
      feLogger.debug("dashboard", "timing", { label, ms });
    }
  };

  function CustomLegend() {
    const legendItems = [
      { value: "Altbau", color: "#e2001a" },
      { value: "Neubau", color: "#434343ff" },
    ];
    return (
      <div className="custom-legend">
        {legendItems.map((entry) => {
          const isActive = visibleLines[entry.value];
          return (
            <span
              key={entry.value}
              onClick={() => handleLegendClick({ dataKey: entry.value })}
              style={{
                marginRight: 16,
                cursor: "pointer",
                color: isActive ? entry.color : "#bbb",
                textDecoration: isActive ? "none" : "line-through",
                opacity: isActive ? 1 : 0.5,
                fontWeight: isActive ? "bold" : "normal",
                userSelect: "none"
              }}
            >
              <svg width="14" height="14" style={{ marginRight: 4, verticalAlign: "middle" }}>
                <rect
                  width="14"
                  height="14"
                  fill={isActive ? entry.color : "#eee"}
                  stroke={isActive ? entry.color : "#bbb"}
                  strokeWidth="2"
                />
              </svg>
              {entry.value}
            </span>
          );
        })}
      </div>
    );
  }

  function handleLegendClick({ dataKey }) {
    setVisibleLines((prev) => {
      const next = { ...prev, [dataKey]: !prev[dataKey] };
      feLogger.info("dashboard", "legend-toggle", { line: dataKey, enabled: next[dataKey] });
      return next;
    });
  }

  // Log interval changes
  useEffect(() => {
    feLogger.debug("dashboard", "interval-change", { selectedInterval });
  }, [selectedInterval]);

  // Fetch warning thresholds from the API
  useEffect(() => {
    const fetchThresholds = async () => {
      feLogger.debug("dashboard", "thresholds-fetch-start", {});
      await timeAsync("thresholds", async () => {
        try {
          const json = await api.get("/thresholds");
          if (json.status === "success" && Array.isArray(json.data) && json.data.length > 0) {
            setWarningThresholds(mapApiToUi(json.data[0]));
            feLogger.info("dashboard", "thresholds-loaded", { count: json.data.length });
          } else {
            feLogger.warn("dashboard", "no-thresholds", { json });
          }
        } catch (err) {
          feLogger.error("dashboard", "thresholds-failed", { error: String(err) });
        }
      });
    };
    fetchThresholds();
  }, []);

  // Fetch current data from the API
  useEffect(() => {
    let intervalId;
    const fetchData = async () => {
      feLogger.debug("dashboard", "current-fetch-start", {});
      await timeAsync("current-latest", async () => {
      try {
        setCurrentError(null);
        const [altbauJson, neubauJson] = await Promise.all([
          api.get("/devices/1/latest"),
          api.get("/devices/2/latest"),
        ]);

        if (altbauJson.status !== "success" || neubauJson.status !== "success") {
          setCurrentError("Aktuelle Messwerte konnten nicht geladen werden.");
          feLogger.warn("dashboard", "current-error", {
            altbau: altbauJson,
            neubau: neubauJson,
          });
          return;
        }

        const mapped = {
          Altbau: {
            Temperatur: parseFloat(altbauJson.data.temperature),
            Luftfeuchtigkeit: parseFloat(altbauJson.data.humidity),
            Pollen: altbauJson.data.pollen,
            Feinstaub: altbauJson.data.particulate_matter,
            timestamp: altbauJson.data.unix_timestamp_seconds,
          },
          Neubau: {
            Temperatur: parseFloat(neubauJson.data.temperature),
            Luftfeuchtigkeit: parseFloat(neubauJson.data.humidity),
            Pollen: neubauJson.data.pollen,
            Feinstaub: neubauJson.data.particulate_matter,
            timestamp: neubauJson.data.unix_timestamp_seconds,
          },
        };
        setCurrentData(mapped);
        feLogger.debug("dashboard", "current-fetched", {
          altbauTs: mapped.Altbau.timestamp,
          neubauTs: mapped.Neubau.timestamp,
        });
        } catch (err) {
          setCurrentError("Aktuelle Messwerte konnten nicht geladen werden.");
          feLogger.error("dashboard", "current-failed", { error: String(err) });
        }
      });
    };

    fetchData();
    intervalId = setInterval(fetchData, 30000);
    return () => clearInterval(intervalId);
  }, []);

  // Fetch historical data for the selected interval
  useEffect(() => {
    let intervalId;
  
    async function fetchChartData() {
      feLogger.debug("dashboard", "chart-fetch-start", { selectedInterval });
      await timeAsync("chart-" + selectedInterval, async () => {
        try {
          setChartError(null);
          const newChartData = {};
          let errorMessage = null;

          for (const metric of metrics) {
            const apiMetric = {
              Temperatur: "temperature",
              Luftfeuchtigkeit: "humidity",
              Pollen: "pollen",
              Feinstaub: "particulate_matter"
            }[metric];

            const { start, end } = getIntervalRange(selectedInterval);
            const json = await api.get(
              `/comparison?device_1=1&device_2=2&metric=${apiMetric}&start=${start}&end=${end}&buckets=360`
            );

            if (json.status === "success") {
              const altbauData = insertGapsInSingleDeviceData(json.device_1, gapSeconds);
              const neubauData = insertGapsInSingleDeviceData(json.device_2, gapSeconds);
              newChartData[metric] = { altbauData, neubauData };

              const nullsAlt = altbauData.filter(d => d.value == null).length;
              const nullsNeu = neubauData.filter(d => d.value == null).length;
              feLogger.debug("dashboard", "chart-series", {
                metric,
                altbauPoints: altbauData.length,
                neubauPoints: neubauData.length,
                altbauNulls: nullsAlt,
                neubauNulls: nullsNeu
              });
            } else {
              errorMessage = json.message || "Diagrammdaten konnten nicht geladen werden.";
              newChartData[metric] = { altbauData: [], neubauData: [] };
              feLogger.warn("dashboard", "chart-error", { metric, json });
            }
          }

          setChartError(errorMessage || null);
          setChartData(newChartData);
          window.selectedInterval = selectedInterval;
          feLogger.info("dashboard", "chart-fetched", { metrics: metrics.length, selectedInterval });
        } catch (err) {
          setChartError("Diagrammdaten konnten nicht geladen werden.");
          feLogger.error("dashboard", "chart-failed", { error: String(err), selectedInterval });
        }
      });
    }

    fetchChartData();
    intervalId = setInterval(fetchChartData, 30000);
    return () => clearInterval(intervalId);
  }, [selectedInterval, gapSeconds]);

  const { start: intervalStart, end: intervalEnd } = getIntervalRange(selectedInterval);

  return (
    <div className="dashboard-wrapper">
      <div className="dashboard-container">
        <section className="current-values">
          <h2 className="section-title">Aktuelle Messwerte</h2>
          {currentError ? (
            <div className="chart-error">{currentError}</div>
          ) : !currentData || !warningThresholds ? (
            <p>Lade aktuelle Messwerte...</p>
          ) : (
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
                      <td className={getWarningClass(warningThresholds, metric, currentData.Altbau[metric])}>
                        {currentData.Altbau[metric] || "—"} {currentData.Altbau[metric] ? metricUnits[metric] : ""}
                      </td>
                      <td className={getWarningClass(warningThresholds, metric, currentData.Neubau[metric])}>
                        {currentData.Neubau[metric] || "—"} {currentData.Neubau[metric] ? metricUnits[metric] : ""}
                      </td>
                    </tr>
                  ))}
                      <tr>
                        <td style={{ fontWeight: "bold", color: "#555" }}>Zeitstempel</td>
                        <td style={{ color: "#555" }}>
                          {currentData.Altbau.timestamp
                            ? formatCurrentTimestamp(currentData.Altbau.timestamp)
                            : "—"}
                        </td>
                        <td style={{ color: "#555" }}>
                          {currentData.Neubau.timestamp
                            ? formatCurrentTimestamp(currentData.Neubau.timestamp)
                            : "—"}
                        </td>
                      </tr>
                </tbody>
              </table>
            </div>
          )}

          <div className="button-container">
            <button onClick={() => navigate("/warnwerte")} className="btn">
              Warnungen ändern
            </button>
          </div>
        </section>

        <section className="chart-section">
          <h2 className="section-title">Verlauf</h2>
          {chartError && (
            <div className="chart-error">{chartError}</div>
          )}
          <div className="interval-buttons">
            {intervals.map((key) => (
              <button
                key={key}
                className={`interval-btn ${selectedInterval === key ? "active" : ""}`}
                onClick={() => setSelectedInterval(key)}
              >
                {key === "30min" ? "30 Minuten"
                  : key === "1h" ? "1 Stunde"
                  : key === "3h" ? "3 Stunden"
                  : key === "6h" ? "6 Stunden"
                  : key === "12h" ? "12 Stunden"
                  : key === "1d" ? "1 Tag"
                  : key === "1w" ? "1 Woche"
                  : "1 Monat"}
              </button>
            ))}
          </div>
        <div className="charts-grid">
          {metrics.map((metric) => {
            const data = chartData[metric] || {};
            const allData = [...(data.altbauData || []), ...(data.neubauData || [])];
            const hasData = allData.length > 0;
            const yAxisDomain = hasData ? getMinMax(data, ["altbauData", "neubauData"], 0.05, metric) : [0, 100];
            const hasAltbauData = (data.altbauData || []).some(d => typeof d.value === "number");
            const hasNeubauData = (data.neubauData || []).some(d => typeof d.value === "number");

            return (
              <div key={metric} className="chart-card"
                onClick={() => { feLogger.info("dashboard", "modal-open", { metric }); setOpenChart(metric); }}
                style={{ cursor: "pointer" }}
                title="Für Großansicht klicken"
              >
                <h3 className="chart-title">{metric}</h3>
                {!hasData ? (
                    <div className="chart-empty">
                      Keine Daten für den gewählten Zeitraum und die gewählte Metrik.<br />
                      Bitte Zeitraum oder Metrik ändern.
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart>
                        <XAxis
                          dataKey="timestamp"
                      type="number"
                      domain={[intervalStart, intervalEnd]}
                      tickFormatter={formatXAxisLabelFromTimestamp}
                      minTickGap={20}
                    />
                    <YAxis
                      width={70}
                      domain={yAxisDomain}
                      label={{
                        value: metricUnits[metric],
                        angle: -90,
                        position: 'insideLeft',
                        offset: 10,
                        style: { textAnchor: 'middle' }
                      }}
                    />
                    <Tooltip content={<CustomTooltip unit={metricUnits[metric]} metric={metric} />} />
                    <Legend content={<CustomLegend />} />
                    {visibleLines["Altbau"] && hasAltbauData && (
                      <Line
                        data={data.altbauData}
                        dataKey="value"
                        name="Altbau"
                        stroke="#e2001a"
                        dot={false}
                      />
                    )}
                    {visibleLines["Neubau"] && hasNeubauData && (
                      <Line
                        data={data.neubauData}
                        dataKey="value"
                        name="Neubau"
                        stroke="#434343ff"
                        dot={false}
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
                  )}
              </div>
            );
          })}
        </div>
        </section>
      </div>

      {openChart && (
        <div className="chart-modal" onClick={() => setOpenChart(null)}>
          <div className="chart-modal-content" onClick={e => e.stopPropagation()}>
            <button
            className="chart-modal-close"
            onClick={() => { feLogger.info("dashboard", "modal-close", { metric: openChart }); setOpenChart(null); }}
            aria-label="Schließen"
            >
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <line x1="7" y1="7" x2="21" y2="21" stroke="currentColor" strokeWidth="2"/>
                <line x1="21" y1="7" x2="7" y2="21" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </button>
            <h3 className="chart-title">{openChart}</h3>
            {(() => {
            const data = chartData[openChart] || {};
            const allData = [...(data.altbauData || []), ...(data.neubauData || [])];
            const hasData = allData.length > 0;
            const yAxisDomain = hasData ? getMinMax(data, ["altbauData", "neubauData"], 0.05, openChart) : [0, 100];
            const hasAltbauData = (data.altbauData || []).some(d => typeof d.value === "number");
            const hasNeubauData = (data.neubauData || []).some(d => typeof d.value === "number");

            if (!hasData) {
              return (
                <div className="chart-empty">
                  Keine Daten für den gewählten Zeitraum und die gewählte Metrik.<br />
                  Bitte Zeitraum oder Metrik ändern.
                </div>
              );
            }

            return (
            <ResponsiveContainer width="100%" height={300}>
                  <LineChart>
                    <XAxis
                      dataKey="timestamp"
                      type="number"
                      domain={[intervalStart, intervalEnd]}
                      tickFormatter={formatXAxisLabelFromTimestamp}
                      minTickGap={20}
                    />
                    <YAxis
                      width={70}
                      domain={yAxisDomain}
                      label={{
                        value: metricUnits[openChart],
                        angle: -90,
                        position: 'insideLeft',
                        offset: 10,
                        style: { textAnchor: 'middle' }
                      }}
                    />
                    <Tooltip content={<CustomTooltip unit={metricUnits[openChart]} metric={openChart} />} />
                    <Legend content={<CustomLegend />} />
                    {visibleLines["Altbau"] && hasAltbauData && (
                      <Line
                        data={data.altbauData}
                        dataKey="value"
                        name="Altbau"
                        stroke="#e2001a"
                        dot={false}
                      />
                    )}
                    {visibleLines["Neubau"] && hasNeubauData && (
                      <Line
                        data={data.neubauData}
                        dataKey="value"
                        name="Neubau"
                        stroke="#434343ff"
                        dot={false}
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
            );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}