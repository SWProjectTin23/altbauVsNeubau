#ifndef SENSOR_READER_H
#define SENSOR_READER_H

#include <Arduino.h>




void sensorInit();
void sensorReadByte();
bool hasDataToSend();
void getAverages(uint16_t &pm25Avg, uint16_t &pm10Avg);
void resetAverages();

#endif
