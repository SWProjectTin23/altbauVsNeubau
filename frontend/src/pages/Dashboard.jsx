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

// Define the base API URL
const API_BASE = "http://localhost:5001/api";

// Define the metrics and intervals
const metrics = ["Temperatur", "Luftfeuchtigkeit", "Pollen", "Feinpartikel"];

const metricUnits = {
  Temperatur: "°C",
  Luftfeuchtigkeit: "%",
  Pollen: "µg/m³",
  Feinpartikel: "µg/m³",
};

const intervals = ["3h", "1d", "1w", "1m"];

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
  Feinpartikel: {
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
  if (selectedInterval === "3h") start = end - 3 * 3600;
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
    // Füge einen null-Punkt hinzu, um eine Lücke zu erzeugen, wenn die Zeitlücke zu groß ist
    if (i > 0 && (d.timestamp - data[i - 1].timestamp) > gapSeconds) {
      result.push({ timestamp: d.timestamp, value: null });
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
  const gapMap = { "3h": 600, "1d": 3600, "1w": 10800, "1m": 43200 };
  const gapSeconds = gapMap[selectedInterval] || 600;

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
    setVisibleLines((prev) => ({
      ...prev,
      [dataKey]: !prev[dataKey],
    }));
  }

  // Fetch warning thresholds from the API
  useEffect(() => {
    const fetchThresholds = async () => {
      try {
        const res = await fetch(`${API_BASE}/thresholds`);
        const json = await res.json();
        if (json.status === "success" && Array.isArray(json.data) && json.data.length > 0) {
          setWarningThresholds(mapApiToUi(json.data[0]));
        } else {
          console.error("No thresholds available.");
        }
      } catch (err) {
        console.error("Error loading warning thresholds:", err);
      }
    };
    fetchThresholds();
  }, []);

  // Fetch current data from the API
  useEffect(() => {
    let intervalId;
    const fetchData = async () => {
      try {
        setCurrentError(null);
        const [altbauRes, neubauRes] = await Promise.all([
          fetch(`${API_BASE}/devices/1/latest`),
          fetch(`${API_BASE}/devices/2/latest`),
        ]);

        const altbauJson = await altbauRes.json();
        const neubauJson = await neubauRes.json();

        if (altbauJson.status !== "success" || neubauJson.status !== "success") {
          setCurrentError("Aktuelle Messwerte konnten nicht geladen werden.");
          return;
        }

        const mapped = {
          Altbau: {
            Temperatur: parseFloat(altbauJson.data.temperature),
            Luftfeuchtigkeit: parseFloat(altbauJson.data.humidity),
            Pollen: altbauJson.data.pollen,
            Feinpartikel: altbauJson.data.particulate_matter,
            timestamp: altbauJson.data.unix_timestamp_seconds,
          },
          Neubau: {
            Temperatur: parseFloat(neubauJson.data.temperature),
            Luftfeuchtigkeit: parseFloat(neubauJson.data.humidity),
            Pollen: neubauJson.data.pollen,
            Feinpartikel: neubauJson.data.particulate_matter,
            timestamp: neubauJson.data.unix_timestamp_seconds,
          },
        };
        setCurrentData(mapped);
      } catch (err) {
        setCurrentError("Aktuelle Messwerte konnten nicht geladen werden.");
      }
    };

    fetchData();
    intervalId = setInterval(fetchData, 30000);
    return () => clearInterval(intervalId);
  }, []);

  // Fetch historical data for the selected interval
  useEffect(() => {
    let intervalId;
  
    async function fetchChartData() {
      try {
        setChartError(null);
        const newChartData = {};
        let errorMessage = null;
        for (const metric of metrics) {
          const apiMetric = {
            Temperatur: "temperature",
            Luftfeuchtigkeit: "humidity",
            Pollen: "pollen",
            Feinpartikel: "particulate_matter"
          }[metric];
          const { start, end } = getIntervalRange(selectedInterval);

          const url = `${API_BASE}/comparison?device_1=1&device_2=2&metric=${apiMetric}&start=${start}&end=${end}&buckets=360`;
          const res = await fetch(url);
          const json = await res.json();

          if (json.status === "success") {
            // Separat die Daten für jedes Gerät verarbeiten
            const altbauData = insertGapsInSingleDeviceData(json.device_1, gapSeconds);
            const neubauData = insertGapsInSingleDeviceData(json.device_2, gapSeconds);
            
            newChartData[metric] = { altbauData, neubauData };
          } else {
            errorMessage = json.message || "Diagrammdaten konnten nicht geladen werden.";
            newChartData[metric] = { altbauData: [], neubauData: [] };
          }
        }
        if (errorMessage) {
          setChartError(errorMessage);
        } else {
          setChartError(null);
        }
        setChartData(newChartData);
        window.selectedInterval = selectedInterval;
      } catch (err) {
        setChartError("Diagrammdaten konnten nicht geladen werden.");
      }
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
                {key === "3h" ? "3 Stunden" : key === "1d" ? "1 Tag" : key === "1w" ? "1 Woche" : "1 Monat"}
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
                onClick={() => setOpenChart(metric)}
                style={{ cursor: "pointer" }}
                title="Für Großansicht klicken"
              >
                <h3 className="chart-title">{metric}</h3>
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
            onClick={() => setOpenChart(null)}
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