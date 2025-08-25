#include "sensor_reader.h"
#include <Wire.h>
#include "Adafruit_HTU21DF.h"

#define BUFFER_SIZE 20

Adafruit_HTU21DF htu = Adafruit_HTU21DF();

#define ADT7410_ADDR 0x48

static uint8_t buffer[BUFFER_SIZE];
static uint8_t bufferIndex = 0;
static uint32_t pm25Sum = 0;
static uint32_t pm10Sum = 0;
static uint16_t packetCount = 0;

static float temperatureSum = 0.0;
static unsigned int temperatureCount = 0;
static bool temperatureSensorAvailable = true;

static float humiditySum = 0.0;
static unsigned int humidityCount = 0;
static bool humiditySensorAvailable = true;

static bool validatePacket() {
  uint8_t sum = 0;
  for (int i = 0; i < BUFFER_SIZE; i++) {
    sum += buffer[i];
  }
  return (sum & 0xFF) == 0;
}

static void parsePacket(uint16_t &pm25, uint16_t &pm10) {
  pm25 = (buffer[5] << 8) | buffer[6];
  uint16_t pm10_raw = (buffer[9] << 8) | buffer[10];
  float factor = max(1.0, (float)pm10_raw / (float)pm25 / 5.0);
  pm10 = (int)(pm10_raw / factor);
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
      } else {
        Serial.println("Feinstaubsensor: ungültiges Paket!");
      }
      bufferIndex = 0;
    }
  }
}

// Temperatur vom ADT7410 per Wire
float readADT7410() {
  Wire.beginTransmission(ADT7410_ADDR);
  Wire.write(0x00); // Temperatur-Register
  Wire.endTransmission();

  Wire.requestFrom(ADT7410_ADDR, 2);
  if (Wire.available() < 2) return NAN;

  uint16_t raw = (Wire.read() << 8) | Wire.read();
  raw >>= 3; // 13-bit Mode
  float tempC = raw * 0.0625; 
  return tempC;
}

void readTemperature() {
  if (!temperatureSensorAvailable) return;
  float c = readADT7410();
  if (isnan(c)) {
    temperatureSensorAvailable = false;
    Serial.println("Temperatursensor nicht verfügbar!");
    return;
  }
  temperatureSum += c;
  temperatureCount++;
}

void readHumidity() {
  if (!humiditySensorAvailable) return;
  float h = htu.readHumidity();
  if (isnan(h)) {
    humiditySensorAvailable = false;
    Serial.println("Feuchtigkeitssensor nicht verfügbar!");
    return;
  }
  humiditySum += h;
  humidityCount++;
}

void getAverages(uint16_t &pm25Avg, uint16_t &pm10Avg, float &temperatureAvg, float &humidityAvg) {
  if (packetCount > 0) {
    pm25Avg = pm25Sum / packetCount;
    pm10Avg = pm10Sum / packetCount;
  } else {
    pm25Avg = 0;
    pm10Avg = 0;
  }
  if (temperatureSensorAvailable && temperatureCount > 0) {
    temperatureAvg = temperatureSum / temperatureCount;
  } else {
    temperatureAvg = 0.0;
  }
  if (humiditySensorAvailable && humidityCount > 0) {
    humidityAvg = humiditySum / humidityCount;
  } else {
    humidityAvg = 0.0;
  }
}

void resetAverages() {
  pm25Sum = 0;
  pm10Sum = 0;
  packetCount = 0;
  temperatureSum = 0.0;
  temperatureCount = 0;
  humiditySum = 0.0;
  humidityCount = 0;
}

void tempsensorStartup() {
  Wire.begin();
  // ADT7410-Test: Ist Sensor erreichbar?
  Wire.beginTransmission(ADT7410_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println("Temperatursensor (ADT7410) nicht gefunden, läuft ohne Temperatur!");
    temperatureSensorAvailable = false;
    return;
  }
  temperatureSensorAvailable = true;
  Serial.println("ADT7410 gefunden.");
}

void humiditySensorStartup() {
  if (!htu.begin()) {
    Serial.println("Feuchtigkeitssensor (HTU21D-F) nicht gefunden, läuft ohne Feuchtigkeit!");
    humiditySensorAvailable = false;
    return;
  }
  humiditySensorAvailable = true;
  Serial.println("HTU21D-F gefunden.");
}

