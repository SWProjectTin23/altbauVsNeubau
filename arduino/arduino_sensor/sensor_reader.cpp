#include "sensor_reader.h"

#define BUFFER_SIZE 20

static uint8_t buffer[BUFFER_SIZE];
static uint8_t bufferIndex = 0;
static uint32_t pm25Sum = 0;
static uint32_t pm10Sum = 0;
static uint16_t packetCount = 0;


static bool validatePacket() {
  uint8_t sum = 0;
  for (int i = 0; i < BUFFER_SIZE; i++) {
    sum += buffer[i];
  }
  return (sum & 0xFF) == 0;
}

static void parsePacket(uint16_t &pm25, uint16_t &pm10) {
  pm25 = (buffer[5] << 8) | buffer[6];
  pm10 = (buffer[9] << 8) | buffer[10];
}

void sensorReadByte() {
  if (Serial1.available()) {
    uint8_t b = Serial1.read();
    buffer[bufferIndex++] = b;

    if (bufferIndex == BUFFER_SIZE) {
      if (validatePacket()) {
        uint16_t pm25, pm10;
        parsePacket(pm25, pm10);
        pm25Sum += pm25;
        pm10Sum += pm10;
        packetCount++;
      }
      bufferIndex = 0;
    }
  }
}


void getAverages(uint16_t &pm25Avg, uint16_t &pm10Avg) {
  if (packetCount > 0) {
    pm25Avg = pm25Sum / packetCount;
    pm10Avg = pm10Sum / packetCount;
  } else {
    pm25Avg = 0;
    pm10Avg = 0;
  }
}

void resetAverages() {
  pm25Sum = 0;
  pm10Sum = 0;
  packetCount = 0;
}
