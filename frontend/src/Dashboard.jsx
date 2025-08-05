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

const API_BASE = "http://localhost:5001/api";

const metrics = ["Temperatur", "Luftfeuchtigkeit", "Pollen", "Feinpartikel"];
const intervals = ["3h", "1d", "1w", "1m"];

const mockData = {
  history: {
    "3h": {
      Temperatur: [
        { time: "10:00", Altbau: 20, Neubau: 22 },
        { time: "11:00", Altbau: 21, Neubau: 23 },
        { time: "12:00", Altbau: 22, Neubau: 23.5 },
      ],
      Luftfeuchtigkeit: [
        { time: "10:00", Altbau: 55, Neubau: 65 },
        { time: "11:00", Altbau: 56, Neubau: 66 },
        { time: "12:00", Altbau: 58, Neubau: 66.5 },
      ],
      Pollen: [
        { time: "10:00", Altbau: 50, Neubau: 200 },
        { time: "11:00", Altbau: 52, Neubau: 205 },
        { time: "12:00", Altbau: 54, Neubau: 210 },
      ],
      Feinpartikel: [
        { time: "10:00", Altbau: 15, Neubau: 8 },
        { time: "11:00", Altbau: 15.5, Neubau: 8.5 },
        { time: "12:00", Altbau: 16, Neubau: 9 },
      ],
    },
    "1d": {
      Temperatur: [
        { time: "00:00", Altbau: 18, Neubau: 20 },
        { time: "06:00", Altbau: 19, Neubau: 21 },
        { time: "12:00", Altbau: 22, Neubau: 23.5 },
        { time: "18:00", Altbau: 21, Neubau: 22.5 },
        { time: "23:59", Altbau: 20, Neubau: 21.5 },
      ],
      Luftfeuchtigkeit: [
        { time: "00:00", Altbau: 50, Neubau: 60 },
        { time: "06:00", Altbau: 52, Neubau: 62 },
        { time: "12:00", Altbau: 58, Neubau: 66.5 },
        { time: "18:00", Altbau: 56, Neubau: 65 },
        { time: "23:59", Altbau: 54, Neubau: 64 },
      ],
      Pollen: [
        { time: "00:00", Altbau: 40, Neubau: 180 },
        { time: "06:00", Altbau: 45, Neubau: 190 },
        { time: "12:00", Altbau: 54, Neubau: 210 },
        { time: "18:00", Altbau: 52, Neubau: 205 },
        { time: "23:59", Altbau: 50, Neubau: 200 },
      ],
      Feinpartikel: [
        { time: "00:00", Altbau: 13, Neubau: 7 },
        { time: "06:00", Altbau: 14, Neubau: 7.5 },
        { time: "12:00", Altbau: 16, Neubau: 9 },
        { time: "18:00", Altbau: 15, Neubau: 8.5 },
        { time: "23:59", Altbau: 14.5, Neubau: 8 },
      ],
    },
    "1w": {
      Temperatur: [
        { time: "Mon", Altbau: 18, Neubau: 21 },
        { time: "Tue", Altbau: 20, Neubau: 22 },
        { time: "Wed", Altbau: 21, Neubau: 23 },
        { time: "Thu", Altbau: 19, Neubau: 21.5 },
        { time: "Fri", Altbau: 22, Neubau: 24 },
        { time: "Sat", Altbau: 20.5, Neubau: 22.5 },
        { time: "Sun", Altbau: 21.5, Neubau: 23 },
      ],
      Luftfeuchtigkeit: [...Array(7)].map((_, i) => ({ time: `Day ${i + 1}`, Altbau: 50 + i, Neubau: 60 + i })),
      Pollen: [...Array(7)].map((_, i) => ({ time: `Day ${i + 1}`, Altbau: 40 + i * 2, Neubau: 180 + i * 5 })),
      Feinpartikel: [...Array(7)].map((_, i) => ({ time: `Day ${i + 1}`, Altbau: 13 + i * 0.5, Neubau: 7 + i * 0.3 })),
    },
    "1m": {
      Temperatur: [...Array(30)].map((_, i) => ({ time: `Tag ${i + 1}`, Altbau: 18 + (i % 5), Neubau: 21 + (i % 3) })),
      Luftfeuchtigkeit: [...Array(30)].map((_, i) => ({ time: `Tag ${i + 1}`, Altbau: 50 + (i % 10), Neubau: 60 + (i % 8) })),
      Pollen: [...Array(30)].map((_, i) => ({ time: `Tag ${i + 1}`, Altbau: 40 + i, Neubau: 180 + i * 2 })),
      Feinpartikel: [...Array(30)].map((_, i) => ({ time: `Tag ${i + 1}`, Altbau: 13 + (i % 4), Neubau: 7 + (i % 3) })),
    },
  },
};

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


const getWarningClass = (thresholds, metric, value) => {
  if (!thresholds || !thresholds[metric]) return "";
  const t = thresholds[metric];
  if (value < t.redLow || value > t.redHigh) return "warn-red";
  if (value < t.yellowLow || value > t.yellowHigh) return "warn-yellow";
  return "";
};

export default function Dashboard() {
  const [selectedInterval, setSelectedInterval] = useState("3h");
  const [currentData, setCurrentData] = useState(null);
  const [warningThresholds, setWarningThresholds] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchThresholds = async () => {
      try {
        const res = await fetch(`${API_BASE}/thresholds`);
        const json = await res.json();
        if (json.status === "success" && Array.isArray(json.data) && json.data.length > 0) {
          setWarningThresholds(mapApiToUi(json.data[0]));
        } else {
          console.error("Keine Warnwerte verfügbar.");
        }
      } catch (err) {
        console.error("Fehler beim Laden der Warnwerte:", err);
      }
    };
    fetchThresholds();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [altbauRes, neubauRes] = await Promise.all([
          fetch(`${API_BASE}/devices/1/latest`),
          fetch(`${API_BASE}/devices/2/latest`),
        ]);

        const altbauJson = await altbauRes.json();
        const neubauJson = await neubauRes.json();

        if (altbauJson.status !== "success" || neubauJson.status !== "success") {
          console.error("API status error");
          return;
        }

        const mapped = {
          Altbau: {
            Temperatur: parseFloat(altbauJson.data.temperature),
            Luftfeuchtigkeit: parseFloat(altbauJson.data.humidity),
            Pollen: altbauJson.data.pollen,
            Feinpartikel: altbauJson.data.particulate_matter,
          },
          Neubau: {
            Temperatur: parseFloat(neubauJson.data.temperature),
            Luftfeuchtigkeit: parseFloat(neubauJson.data.humidity),
            Pollen: neubauJson.data.pollen,
            Feinpartikel: neubauJson.data.particulate_matter,
          },
        };

        setCurrentData(mapped);
      } catch (err) {
        console.error("Fehler beim Laden der aktuellen Daten:", err);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="dashboard-wrapper">
      <div className="dashboard-container">
        <section className="current-values">
          <h2 className="section-title">Aktuelle Messwerte</h2>
          {!currentData || !warningThresholds ? (
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
                        {currentData.Altbau[metric]}
                      </td>
                      <td className={getWarningClass(warningThresholds, metric, currentData.Neubau[metric])}>
                        {currentData.Neubau[metric]}
                      </td>
                    </tr>
                  ))}
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
            {metrics.map((metric) => (
              <div key={metric} className="chart-card">
                <h3 className="chart-title">{metric}</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={mockData.history[selectedInterval][metric]}>
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="Altbau" stroke="#602383" />
                    <Line type="monotone" dataKey="Neubau" stroke="#1750BA" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
