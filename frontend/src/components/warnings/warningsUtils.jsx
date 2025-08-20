// Map API response to UI format
export const mapApiToUi = (data) => ({
  Temperatur: {
    redLow: data.temperature_min_hard,    // min_hard = rot
    yellowLow: data.temperature_min_soft, // min_soft = gelb
    yellowHigh: data.temperature_max_soft,// max_soft = gelb
    redHigh: data.temperature_max_hard,   // max_hard = rot
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

// Map the UI format to API format
export const mapUiToApi = (uiData) => ({
  temperature_min_hard: uiData.Temperatur.redLow,
  temperature_min_soft: uiData.Temperatur.yellowLow,
  temperature_max_soft: uiData.Temperatur.yellowHigh,
  temperature_max_hard: uiData.Temperatur.redHigh,

  humidity_min_hard: uiData.Luftfeuchtigkeit.redLow,
  humidity_min_soft: uiData.Luftfeuchtigkeit.yellowLow,
  humidity_max_soft: uiData.Luftfeuchtigkeit.yellowHigh,
  humidity_max_hard: uiData.Luftfeuchtigkeit.redHigh,

  pollen_min_hard: uiData.Pollen.redLow,
  pollen_min_soft: uiData.Pollen.yellowLow,
  pollen_max_soft: uiData.Pollen.yellowHigh,
  pollen_max_hard: uiData.Pollen.redHigh,

  particulate_matter_min_hard: uiData.Feinstaub.redLow,
  particulate_matter_min_soft: uiData.Feinstaub.yellowLow,
  particulate_matter_max_soft: uiData.Feinstaub.yellowHigh,
  particulate_matter_max_hard: uiData.Feinstaub.redHigh,
});

  // Validate the warning thresholds
export const validateWarnings = (warnings) => {
  for (const [metric, levels] of Object.entries(warnings)) {
    if (levels.redLow >= levels.yellowLow) {
      return `Bei "${metric}": "Warnwert niedrig rot" darf nicht größer als "Warnwert niedrig gelb" sein.`;
    }
    if (levels.redLow >= levels.redHigh) {
      return `Bei "${metric}": "Warnwert niedrig rot" muss kleiner als "Warnwert hoch rot" sein.`;
    }
    if (levels.yellowLow >= levels.yellowHigh) {
      return `Bei "${metric}": "Warnwert niedrig gelb" muss kleiner als "Warnwert hoch gelb" sein.`;
    }
  }
  return null;
};