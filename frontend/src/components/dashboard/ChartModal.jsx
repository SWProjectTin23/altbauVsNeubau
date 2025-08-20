import React from "react";
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, Line } from "recharts";
import CustomTooltip from "./CustomTooltip";
import CustomLegend from "./CustomLegend";
import { formatXAxisLabelFromTimestamp } from "./dashboardUtils";

export default function ChartModal({
  openChart,
  chartData,
  intervalStart,
  intervalEnd,
  metricUnits,
  visibleLines,
  handleLegendClick,
  getMinMax,
  onClose
}) {
  if (!openChart) return null;

  const data = chartData[openChart] || {};
  const allData = [...(data.altbauData || []), ...(data.neubauData || [])];
  const hasData = allData.length > 0;
  const yAxisDomain = hasData ? getMinMax(data, ["altbauData", "neubauData"], 0.05, openChart) : [0, 100];
  const hasAltbauData = (data.altbauData || []).some(d => typeof d.value === "number");
  const hasNeubauData = (data.neubauData || []).some(d => typeof d.value === "number");

  return (
    <div className="chart-modal" onClick={onClose}>
      <div className="chart-modal-content" onClick={e => e.stopPropagation()}>
        <button
          className="chart-modal-close"
          onClick={onClose}
          aria-label="Schließen"
        >
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <line x1="7" y1="7" x2="21" y2="21" stroke="currentColor" strokeWidth="2"/>
            <line x1="21" y1="7" x2="7" y2="21" stroke="currentColor" strokeWidth="2"/>
          </svg>
        </button>
        <h3 className="chart-title">{openChart}</h3>
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
                  value: metricUnits[openChart],
                  angle: -90,
                  position: 'insideLeft',
                  offset: 10,
                  style: { textAnchor: 'middle' }
                }}
              />
              <Tooltip content={<CustomTooltip unit={metricUnits[openChart]} metric={openChart} />} />
              <Legend content={
                <CustomLegend
                  visibleLines={visibleLines}
                  handleLegendClick={handleLegendClick}
                />
              } />
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
    </div>
  );
}