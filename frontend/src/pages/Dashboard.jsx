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
import '../App.css';
import { api } from "../utils/api";
import { feLogger } from "../logging/logger";

import CurrentValuesTable from "../components/dashboard/CurrentValuesTable";
import CustomLegend from "../components/dashboard/CustomLegend";
import CustomTooltip from "../components/dashboard/CustomTooltip";
import { 
  mapApiToUi, 
  getIntervalRange, 
  insertGapsInSingleDeviceData,
  getMinMax, 
  getWarningClass, 
  formatCurrentTimestamp, 
  formatXAxisLabelFromTimestamp 
} from "../components/dashboard/dashboardUtils";
import ChartModal from "../components/dashboard/ChartModal";
import ChartCard from "../components/dashboard/ChartCard";
import IntervalButtons from "../components/dashboard/IntervalButtons";



// Define the metrics and intervals
const metrics = ["Temperatur", "Luftfeuchtigkeit", "Pollen", "Feinstaub"];

const metricUnits = {
  Temperatur: "°C",
  Luftfeuchtigkeit: "%",
  Pollen: "µg/m³",
  Feinstaub: "µg/m³",
};

// Define the time intervals
const intervals = ["30min", "1h", "3h", "6h", "12h", "1d", "1w", "1m"];

// Dashboard component
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
    "30min": 180,      // 3 Minutes
    "1h": 300,         // 5 Minutes
    "3h": 600,         // 10 Minutes
    "6h": 900,        // 15 Minutes
    "12h": 1800,       // 30 Minutes
    "1d": 3600,        // 1 Hour
    "1w": 10800,       // 3 Hours
    "1m": 43200        // 12 Hours
  };
  // Determine the gap seconds for the selected interval
  const gapSeconds = gapMap[selectedInterval];

  // Timing wrapper for async functions
  const timeAsync = async (label, fn) => {
    const t0 = performance.now();
    try {
      return await fn();
    } finally {
      const ms = +(performance.now() - t0).toFixed(0);
      feLogger.debug("dashboard", "timing", { label, ms });
    }
  };

  // Handle legend item clicks
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

        // Map the API response to the desired format
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

    // Fetch initial data
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

            // Get the time range for the selected interval
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

          // Handle case where all values are missing
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

    // Fetch chart data
    fetchChartData();
    intervalId = setInterval(fetchChartData, 30000);
    return () => clearInterval(intervalId);
  }, [selectedInterval, gapSeconds]);

  // Get the time range for the selected interval
  const { start: intervalStart, end: intervalEnd } = getIntervalRange(selectedInterval);

    return (
    <div className="wrapper">
      <div className="container">
        <section className="current-values">
          <h2 className="section-title">Aktuelle Messwerte</h2>
          {(!currentData || !warningThresholds) ? (
            <p>Lade aktuelle Messwerte...</p>
          ) : (
            <CurrentValuesTable
              metrics={metrics}
              currentData={currentData}
              warningThresholds={warningThresholds}
            />
          )}
          <div className="button-container">
            <button onClick={() => navigate("/warnings")} className="btn">
              Warnungen ändern
            </button>
          </div>
        </section>

        <section className="chart-section">
          <h2 className="section-title">Verlauf</h2>
          {chartError && (
            <div className="chart-error">{chartError}</div>
          )}
          <IntervalButtons
            intervals={intervals}
            selectedInterval={selectedInterval}
            setSelectedInterval={setSelectedInterval}
          />
          <div className="grid-2">
            {metrics.map((metric) => (
              <ChartCard
                key={metric}
                metric={metric}
                data={chartData[metric] || {}}
                intervalStart={intervalStart}
                intervalEnd={intervalEnd}
                metricUnits={metricUnits}
                visibleLines={visibleLines}
                handleLegendClick={handleLegendClick}
                onClick={() => { feLogger.info("dashboard", "modal-open", { metric }); setOpenChart(metric); }}
              />
            ))}
          </div>
        </section>
      </div>

      <ChartModal
        openChart={openChart}
        chartData={chartData}
        intervalStart={intervalStart}
        intervalEnd={intervalEnd}
        metricUnits={metricUnits}
        visibleLines={visibleLines}
        handleLegendClick={handleLegendClick}
        getMinMax={getMinMax}
        onClose={() => { feLogger.info("dashboard", "modal-close", { metric: openChart }); setOpenChart(null); }}
      />
    </div>
  );
}