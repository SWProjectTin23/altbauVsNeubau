#include "data_sender.h"
#include "sensor_reader.h"
#include "WiFiUtils.h"
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
  startupTime = getUnixTime(); 
  sequence = 0;
}

void loop() {
  mqttLoop();
  while (Serial1.available()) {
    sensorReadByte();
  }

  
 //mockReadByte(); delay(50);

   if (millis() - lastAverageTime >= AVERAGE_INTERVAL_MS) {
     checkWiFiConnection(WIFI_SSID, WIFI_PASS);
     uint16_t pm25Avg, pm10Avg;
     getAverages(pm25Avg, pm10Avg);
     sendAverages(startupTime, sequence++, pm25Avg, pm10Avg);
     resetAverages();
     lastAverageTime = millis();
   }
}






