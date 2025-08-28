import React from "react";
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, Line } from "recharts";
import CustomTooltip from "./CustomTooltip";
import CustomLegend from "./CustomLegend";
import { formatXAxisLabelFromTimestamp, getMinMax } from "./dashboardUtils";

export default function ChartCard({
  metric,
  data,
  intervalStart,
  intervalEnd,
  metricUnits,
  visibleLines,
  handleLegendClick,
  onClick,
}) {
  const allData = [...(data.altbauData || []), ...(data.neubauData || [])];
  const hasData = allData.length > 0;
  const yAxisDomain = hasData ? getMinMax(data, ["altbauData", "neubauData"], 0.05, metric) : [0, 100];
  const hasAltbauData = (data.altbauData || []).some(d => typeof d.value === "number");
  const hasNeubauData = (data.neubauData || []).some(d => typeof d.value === "number");

  return (
    <div className="card" onClick={onClick} style={{ cursor: "pointer" }} title="Für Großansicht klicken">
      <h3 className="chart-title">{metric}</h3>
      {!hasData ? (
        <div className="chart-empty">
          Keine Daten für den gewählten Zeitraum und die gewählte Metrik.<br />
          Bitte Zeitraum oder Metrik ändern.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={400}>
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
  );
}