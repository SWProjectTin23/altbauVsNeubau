#include "WifiUtils.h"
#include <WiFiNINA.h>  


void connectToWiFi(const char* ssid, const char* password) {
  int status = WL_IDLE_STATUS;
  WiFi.disconnect();  // Disconnect from any previous connection

  WiFi.begin(ssid, password); // Start the connection to the WiFi network
  unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) { // Wait for connection or timeout after 10 seconds
    delay(500);
    status = WiFi.status();
  }

  if (WiFi.status() == WL_CONNECTED) {
    IPAddress ip = WiFi.localIP();
    Serial.print("Meine lokale IP: ");
    Serial.println(ip);
    return;
  }

  switch (status) {         // Check the status of the WiFi connection
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
void checkWiFiConnection(const char* ssid, const char* password) {    // Check if the WiFi is connected, if not, try to reconnect
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WLAN getrennt – versuche Neuverbindung...");
    connectToWiFi(ssid, password);
  }
}