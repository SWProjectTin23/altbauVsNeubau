#include "Ikea.h"
#include "WiFiUtils.h"
#include "MQTTUtils.h"
#include "secrets.h"
#include "TimeUtils.h"

int startupTime; 
int sequence = 0;

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
  //while (Serial1.available()) {
  //  readByte();
  //}

  
 mockReadByte(); delay(50);

   if (millis() - lastAverageTime >= AVERAGE_INTERVAL_MS && packetCount > 0) {
     checkWiFiConnection(WIFI_SSID, WIFI_PASS);
     sendAverages(startupTime, sequence);
     resetAverages();
     lastAverageTime = millis();
   }
}






