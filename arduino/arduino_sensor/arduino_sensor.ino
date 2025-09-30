#include "data_sender.h"
#include "sensor_reader.h"
#include "WifiUtils.h"
#include "MQTTUtils.h"
#include "secrets.h"
#include "TimeUtils.h"

const unsigned long AVERAGE_INTERVAL_MS = 30000;
int startupTime; 
int sequence = 0;
unsigned long lastAverageTime;

void setup() {
  Serial.begin(115200);
  delay(1000);
  connectToWiFi(WIFI_SSID, WIFI_PASS);
  mqttSetup();
  setupTime();
  Serial1.begin(9600);
  Serial.begin(115200);
  tempsensorStartup();
  humiditySensorStartup();
  startupTime = getUnixTime(); 
  sequence = 0;
}

void loop() {
  mqttLoop();
  while (Serial1.available()) {
    sensorReadByte();
  }

  readTemperature();
  readHumidity();

  if (millis() - lastAverageTime >= AVERAGE_INTERVAL_MS) {
    checkWiFiConnection(WIFI_SSID, WIFI_PASS);
    uint16_t pm25Avg, pm10Avg;
    float temperatureAvg, humidityAvg;
    getAverages(pm25Avg, pm10Avg, temperatureAvg, humidityAvg);
    sendAverages(startupTime, sequence++, pm25Avg, pm10Avg, temperatureAvg, humidityAvg);
    resetAverages();
    lastAverageTime = millis();
  }
}
