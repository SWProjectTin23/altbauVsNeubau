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


static bool validatePacket() {              // Validate the packet by checking the checksum
  uint8_t sum = 0;                          
  for (int i = 0; i < BUFFER_SIZE; i++) {
    sum += buffer[i];
  }
  return (sum & 0xFF) == 0;
}

static void parsePacket(uint16_t &pm25, uint16_t &pm10) {     // Parse the packet to extract PM2.5 and PM10 values
            pm25 = (buffer[5] << 8) | buffer[6];
  uint16_t  pm10_raw = (buffer[9] << 8) | buffer[10];

  float     factor = max(1.0, (float)pm10_raw / (float)pm25 / 5.0);

  pm10 = (int)(pm10_raw / factor);
}

void sensorReadByte() {             // Read the sensor data and write it to the variable
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

void readTemperature() {      // Read the temperature from the sensor
   float c = tempsensor.readTempC();
   temperatureSum += c;
   temperatureCount++;
}  

void getAverages(uint16_t &pm25Avg, uint16_t &pm10Avg, float &temperatureAvg) {       // Calculate the averages of PM2.5, PM10, and temperature
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

void resetAverages() {    // Reset the averages and counters
  pm25Sum = 0;
  pm10Sum = 0;
  packetCount = 0;
  temperatureSum = 0.0;
  temperatureCount = 0;
}

void tempsensorStartup()    // Initialize the temperature sensor
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


 
    
  