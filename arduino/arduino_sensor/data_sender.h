#ifndef DATA_SENDER_H
#define DATA_SENDER_H

#include <Arduino.h>

void senderInit();
void sendSensorData(int value, int startupTime, int timestamp, int sequence, const char* sensorID);
void sendAverages(int startupTime, int sequence, uint16_t pm25Avg, uint16_t pm10Avg);

#endif
