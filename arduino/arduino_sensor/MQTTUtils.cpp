#include "MQTTUtils.h"
#include "secrets.h"
#include <WiFiNINA.h>
#include <PubSubClient.h>

WiFiClient wifiClient1;
PubSubClient client1(wifiClient1);

WiFiClient wifiClient2;
PubSubClient client2(wifiClient2);

// Retry-Timeouts (in ms)
unsigned long mqtt1_next_retry = 0;
unsigned long mqtt2_next_retry = 0;
const unsigned long MQTT_RETRY_INTERVAL = 30000; // 30 Sekunden

void mqttSetup() {
  client1.setServer(MQTT_SERVER, MQTT_PORT);
#ifdef MQTT_SERVER2
  client2.setServer(MQTT_SERVER2, MQTT_PORT2);
#endif
}

bool mqttReconnect(PubSubClient& client, const char* clientName, unsigned long& next_retry) {
  if (client.connected()) return true;
  unsigned long now = millis();
  if (now < next_retry) return false; // Noch nicht wieder versuchen
  bool ok = client.connect(clientName);
  if (!ok) next_retry = now + MQTT_RETRY_INTERVAL;
  else next_retry = 0;
  return ok;
}

void mqttPublish(const char* topic, const char* payload) {
  // Sende an ersten Server
  bool sent1 = false;
  if (!client1.connected()) {
    mqttReconnect(client1, "MKRWiFi1010Client1", mqtt1_next_retry);
  }
  if (client1.connected()) {
    sent1 = client1.publish(topic, payload);
    Serial.print("Nachricht gesendet an MQTT1 ");
    Serial.print(topic);
    Serial.print(": ");
    Serial.println(payload);
  } else {
    Serial.println("MQTT1 nicht verbunden, überspringe Publish.");
  }

#ifdef MQTT_SERVER2
  // Sende an zweiten Server
  bool sent2 = false;
  if (!client2.connected()) {
    mqttReconnect(client2, "MKRWiFi1010Client2", mqtt2_next_retry);
  }
  if (client2.connected()) {
    sent2 = client2.publish(topic, payload);
    Serial.print("Nachricht gesendet an MQTT2 ");
    Serial.print(topic);
    Serial.print(": ");
    Serial.println(payload);
  } else {
    Serial.println("MQTT2 nicht verbunden, überspringe Publish.");
  }
#endif
}

void mqttLoop() {
  client1.loop();
#ifdef MQTT_SERVER2
  client2.loop();
#endif
}
