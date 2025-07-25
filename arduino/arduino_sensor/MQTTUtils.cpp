#include "MQTTUtils.h"
#include "secrets.h"
#include <WiFiNINA.h>
#include <PubSubClient.h>

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void mqttSetup() {
  client.setServer(MQTT_SERVER, MQTT_PORT);
}

bool mqttReconnect() {
  if (client.connected()) return true;

  if (client.connect("MKRWiFi1010Client")) {
    return true;
  } else {
    return false;
  }
}


void mqttPublish(const char* topic, const char* payload) {
  if (!client.connected()) {
    Serial.println("MQTT nicht verbunden – versuche Verbindung...");
    if (!mqttReconnect()) {
      Serial.println("MQTT-Verbindung fehlgeschlagen. Nachricht wird nicht gesendet.");
      return; 
    }
  }

  if (client.publish(topic, payload)) {
    Serial.print("Nachricht gesendet an ");
    Serial.print(topic);
    Serial.print(": ");
    Serial.println(payload);
  } else {
    Serial.print("Fehler beim Senden an ");
    Serial.print(topic);
    Serial.println(".");
  }
}


void mqttLoop() {
  client.loop();
}
