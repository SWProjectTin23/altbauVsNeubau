#ifndef Ikea_H
#define Ikea_H

#include <Arduino.h>

// Globale Konstanten
const uint8_t BUFFER_SIZE = 20;
const unsigned long AVERAGE_INTERVAL_MS = 30000;

// Externe Variablen
extern uint8_t buffer[BUFFER_SIZE];
extern uint8_t bufferIndex;
extern unsigned long lastAverageTime;
extern uint32_t pm25Sum;
extern uint32_t pm10Sum;
extern uint16_t packetCount;

// Funktionsprototypen
void readByte();
bool validatePacket();
void parsePacket(uint16_t &pm25, uint16_t &pm10);
void updateAverages(uint16_t pm25, uint16_t pm10);
void sendAverages(int startupTime, int sequence);
void resetAverages();
void mockReadByte();
void sendSensorData(int value, int startupTime, int timestamp, int sequence, const char* sensorID);

#endif
