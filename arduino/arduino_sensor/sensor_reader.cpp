#include "sensor_reader.h"
#include <Wire.h>
#include "Adafruit_ADT7410.h"

#define BUFFER_SIZE 20

Adafruit_ADT7410 tempsensor = Adafruit_ADT7410();

static uint8_t buffer[BUFFER_SIZE];
static uint8_t bufferIndex = 0;
static uint32_t pm25Sum = 0;
static uint32_t pm10Sum = 0;
static uint16_t packetCount = 0;
static float temperatureSum = 0.0;
static unsigned int temperatureCount = 0;


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

void readTemperature() {
   float c = tempsensor.readTempC();
   temperatureSum += c;
   temperatureCount++;
}  

void getAverages(uint16_t &pm25Avg, uint16_t &pm10Avg, float &temperatureAvg) {
  if (packetCount > 0) {
    pm25Avg = pm25Sum / packetCount;
    pm10Avg = pm10Sum / packetCount;
    temperatureAvg = temperatureSum / temperatureCount;
  } else {
    pm25Avg = 0;
    pm10Avg = 0;
    temperatureAvg = 0.0;
  }
}

void resetAverages() {
  pm25Sum = 0;
  pm10Sum = 0;
  packetCount = 0;
  temperatureSum = 0.0;
  temperatureCount = 0;
}

void tempsensorStartup()
{
  if (!tempsensor.begin())
  {
    Serial.println("Could not find a valid ADT7410 sensor, check wiring!");
    while (1)
      ;
  }
  delay(250);

  tempsensor.setResolution(ADT7410_16BIT);
  Serial.print("Resolution = ");
  switch (tempsensor.getResolution())
  {
  case ADT7410_13BIT:
    Serial.print("13 ");
    break;
  case ADT7410_16BIT:
    Serial.print("16 ");
    break;
  default:
    Serial.print("??");
  }
  Serial.println("bits");
}


 
    
  