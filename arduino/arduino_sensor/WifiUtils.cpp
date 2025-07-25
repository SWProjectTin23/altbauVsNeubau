#include "WifiUtils.h"
#include <WiFiNINA.h>  


void connectToWiFi(const char* ssid, const char* password) {
  int status = WL_IDLE_STATUS;
  WiFi.disconnect();  // Sauber starten

  WiFi.begin(ssid, password);
  unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
    delay(500);
    status = WiFi.status();
  }

  if (WiFi.status() == WL_CONNECTED) {
    IPAddress ip = WiFi.localIP();
    Serial.print("Meine lokale IP: ");
    Serial.println(ip);
    return;
  }

  switch (status) {
    case WL_NO_SSID_AVAIL:
      Serial.println("SSID nicht gefunden");
      break;
    case WL_CONNECT_FAILED:
      Serial.println("Verbindung fehlgeschlagen");
      break;
    case WL_CONNECTION_LOST:
      Serial.println("Verbindung verloren");
      break;
    case WL_DISCONNECTED:
      Serial.println("Nicht verbunden");
      break;
    default:
      Serial.print("Status: ");
      Serial.println(status);
      break;
  }

}
void checkWiFiConnection(const char* ssid, const char* password) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WLAN getrennt – versuche Neuverbindung...");
    connectToWiFi(ssid, password);
  }
}