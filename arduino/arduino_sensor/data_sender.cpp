#include "data_sender.h"
#include <ArduinoJson.h>
#include "MQTTUtils.h"
#include "TimeUtils.h"
#include "secrets.h"

// Template-Funktion für beliebige numerische Werte
template<typename T>
void sendSensorData(T value, int startupTime, int timestamp, int sequence, const char* topic) {
  StaticJsonDocument<256> doc;
  doc["timestamp"] = timestamp;
  doc["value"] = value;
  doc["sequence"] = sequence;

  JsonObject meta = doc.createNestedObject("meta");
  meta["firmware"] = "v1.2.3";
  meta["startup"] = startupTime;
  meta["device_id"] = DEVICE_ID;

  char payload[256];
  serializeJson(doc, payload, sizeof(payload));

  mqttPublish(topic, payload);
}

void sendAverages(int startupTime, int sequence, uint16_t pm25Avg, uint16_t pm10Avg, float temperatureAvg) {
  int timestamp = getUnixTime();
  sendSensorData<uint16_t>(pm25Avg, startupTime, timestamp, sequence, "dhbw/ai/si2023/01/ikea/01");
  sendSensorData<uint16_t>(pm10Avg, startupTime, timestamp, sequence, "dhbw/ai/si2023/01/ikea/02");
  sendSensorData<float>(temperatureAvg, startupTime, timestamp, sequence, "dhbw/ai/si2023/01/temperature/01");
}
