// Function to map API data to UI thresholds
export const mapApiToUi = (data) => ({
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

// Function to get the interval range based on the selected interval
export function getIntervalRange(selectedInterval) {
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

// Function to insert gaps in the data of a single device
export function insertGapsInSingleDeviceData(data, gapSeconds) {
  if (!data || data.length === 0) return [];
  const result = [];
  data.forEach((d, i) => {
    if (i > 0) {
      const diff = d.timestamp - data[i - 1].timestamp;
      if (diff > gapSeconds) {
        result.push({ timestamp: data[i - 1].timestamp + gapSeconds, value: null });
      }
    }
    result.push({ timestamp: d.timestamp, value: d.value });
  });
  return result;
} 

// Function to get the minimum and maximum values from the data
export function getMinMax(data, keys, padding = 0.05, metric = "Temperatur") {
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

  // Handle case where all values are missing
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

// Function to get the warning class based on thresholds and metric value
export const getWarningClass = (thresholds, metric, value) => {
  if (!thresholds || !thresholds[metric]) return "";
  const t = thresholds[metric];
  if (value < t.redLow || value > t.redHigh) return "warn-red";
  if (value < t.yellowLow || value > t.yellowHigh) return "warn-yellow";
  return "";
};

// Function to format the X-axis label from a timestamp
export function formatXAxisLabelFromTimestamp(ts) {
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

// Function to format the current timestamp
export function formatCurrentTimestamp(ts) {
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