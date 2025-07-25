#include "Ikea.h"
#include "MQTTUtils.h"
#include "TimeUtils.h"
#include <ArduinoJson.h>


uint8_t buffer[BUFFER_SIZE];
uint8_t bufferIndex = 0;
unsigned long lastAverageTime = 0;
uint32_t pm25Sum = 0;
uint32_t pm10Sum = 0;
uint16_t packetCount = 0;

void sendSensorData(int value, int startupTime, int timestamp, int sequence, const char* sensorID) {
  StaticJsonDocument<256> doc;
  doc["timestamp"] = timestamp;
  doc["value"] = value;
  doc["sequence"] = sequence++;

  JsonObject meta = doc.createNestedObject("meta");
  meta["firmware"] = "v1.2.3";
  meta["startup"] = startupTime;

  char payload[256];
  serializeJson(doc, payload, sizeof(payload));
  char topic[64];
  snprintf(topic, sizeof(topic), "dhbw/ai/si2023/01/ikea/%s", sensorID);
  mqttPublish(topic, payload);

}


void readByte() {
  uint8_t b = Serial1.read();
  buffer[bufferIndex++] = b;

  if (bufferIndex == BUFFER_SIZE) {
    if (validatePacket()) {
      uint16_t pm25, pm10;
      parsePacket(pm25, pm10);
      updateAverages(pm25, pm10);
    }
    bufferIndex = 0;
  }
}

bool validatePacket() {
  uint8_t sum = 0;
  for (int i = 0; i < BUFFER_SIZE; i++) {
    sum += buffer[i];
  }
  return (sum & 0xFF) == 0;
}

void parsePacket(uint16_t &pm25, uint16_t &pm10) {
  pm25 = (buffer[5] << 8) | buffer[6];
  pm10 = (buffer[9] << 8) | buffer[10];
}

void updateAverages(uint16_t pm25, uint16_t pm10) {
  pm25Sum += pm25;
  pm10Sum += pm10;
  packetCount++;
}

void sendAverages(int startupTime, int sequence) {
  Serial.print("PM2.5 = ");
  Serial.print(pm25Sum / packetCount);
  Serial.print(" PM10 = ");
  Serial.println(pm10Sum / packetCount);
  int timestamp = getUnixTime();
  sendSensorData(pm25Sum / packetCount, startupTime, timestamp, sequence, "01");
  sendSensorData(pm10Sum / packetCount, startupTime, timestamp, sequence, "02");
}

void resetAverages() {
  pm25Sum = 0;
  pm10Sum = 0;
  packetCount = 0;
}

void mockReadByte() {
  static const uint8_t testPacket[20] = {
    0x16, 0x11, 0x0B, 0x00, 0x00,
    0x01, 0xF4, 0x00, 0x00,
    0x02, 0x58, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00
  };

  static uint8_t mockIndex = 0;
  static uint8_t packet[20];

  if (mockIndex == 0) {
    memcpy(packet, testPacket, 20);
    uint8_t sum = 0;
    for (int i = 0; i < 19; i++) sum += packet[i];
    packet[19] = -sum;
  }

  buffer[bufferIndex++] = packet[mockIndex++];

  if (bufferIndex == BUFFER_SIZE) {
    if (validatePacket()) {
      uint16_t pm25, pm10;
      parsePacket(pm25, pm10);
      updateAverages(pm25, pm10);
    }
    bufferIndex = 0;
    mockIndex = 0;
  }
}

