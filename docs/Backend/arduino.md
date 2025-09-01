# Arduino Code Dokumentation

Dieses Dokument beschreibt die Struktur und Funktion der Arduino-Skripte im Projekt **altbauVsNeubau**.

## Übersicht

Die Arduino-Skripte dienen dazu, Sensordaten zu erfassen und per MQTT-Protokoll an das zentrale Backend zu senden.

## Hauptfunktionen

- **Initialisierung der Sensoren:** Im `setup()`-Block werden alle angeschlossenen Sensoren initialisiert.
- **WLAN-Verbindung:** Das Board verbindet sich mit dem konfigurierten WLAN.
- **MQTT-Verbindung:** Aufbau und Aufrechterhaltung einer Verbindung zum MQTT-Broker.
- **Datenerfassung:** Im `loop()`-Block werden regelmäßig Messwerte von den Sensoren gelesen.
- **Nachrichtenformat:** Die Messwerte werden als JSON-Objekt formatiert (siehe [ADR 0008](./adr/0008-MQTT-communication-protocol.md)).
- **Versand:** Die JSON-Nachricht wird auf einem projektspezifischen MQTT-Topic veröffentlicht.

## Beispiel für eine MQTT-Nachricht

```json
{
  "timestamp": "1753098733",
  "value": 23.4,
  "sequence": 123,
  "meta": {
    "firmware": "v1.2.3",
    "startup": "1753098730"
  }
}
```

## Wichtige Dateien

- `arduino_sensor.ino`: Hauptprogramm, enthält Setup und Loop.
- `Ikea.cpp`: Konfigurationsdatei für Sensoreinstellungen.
- `WifiUtils.cpp` und `MQTTUtils.cpp`: für das senden an den MQTT-Broker.

## Hinweise

- Die Zugangsdaten für WLAN und MQTT sollten nicht im Repository veröffentlicht werden.
->Im gitignore ist deshalb die secrest.h datei
- Für die Integration neuer Sensoren bitte die bestehenden Strukturen und das Nachrichtenformat beachten.

secrests.h:
```
#ifndef SECRETS_H
#define SECRETS_H

#define WIFI_SSID     "Wifi_SSID"
#define WIFI_PASS     "Wifi_pass"

#define MQTT_SERVER   "isd-gerold.de"
#define MQTT_PORT     1883


#endif
```

