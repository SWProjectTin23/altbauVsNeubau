#include "data_sender.h"
#include <ArduinoJson.h>
#include "MQTTUtils.h"
#include "TimeUtils.h"


void sendSensorData(int value, int startupTime, int timestamp, int sequence, const char* sensorID) {
  StaticJsonDocument<256> doc;
  doc["timestamp"] = timestamp;
  doc["value"] = value;
  doc["sequence"] = sequence;

  JsonObject meta = doc.createNestedObject("meta");
  meta["firmware"] = "v1.2.3";
  meta["startup"] = startupTime;

  char payload[256];
  serializeJson(doc, payload, sizeof(payload));

  char topic[64];
  snprintf(topic, sizeof(topic), "dhbw/ai/si2023/01/ikea/%s", sensorID);
  mqttPublish(topic, payload);
}

void sendAverages(int startupTime, int sequence, uint16_t pm25Avg, uint16_t pm10Avg) {
  int timestamp = getUnixTime();
  sendSensorData(pm25Avg, startupTime, timestamp, sequence, "01");
  sendSensorData(pm10Avg, startupTime, timestamp, sequence, "02");
}
