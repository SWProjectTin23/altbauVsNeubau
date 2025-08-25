#include <Wire.h>
#include "Adafruit_HTU21DF.h"

// HTU21D-F: Humidity
Adafruit_HTU21DF htu = Adafruit_HTU21DF();

// ADT7410: Temperatur (Adresse 0x48)
#define ADT7410_ADDR 0x48

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("Starte Sensor-Test...");

  // HTU21D-F initialisieren
  if (!htu.begin()) {
    Serial.println("Fehler: HTU21D-F nicht gefunden!");
    while (1);
  }
  Serial.println("HTU21D-F gefunden.");

  // ADT7410 initialisieren
  Wire.beginTransmission(ADT7410_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println("Fehler: ADT7410 nicht gefunden!");
    while (1);
  }
  Serial.println("ADT7410 gefunden.");
}

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

void loop() {
  // Humidity vom HTU21D-F
  float humidity = htu.readHumidity();
  if (!isnan(humidity)) {
    Serial.print("Luftfeuchtigkeit: ");
    Serial.print(humidity);
    Serial.println(" %");
  } else {
    Serial.println("Fehler beim Lesen der Luftfeuchtigkeit!");
  }

  // Temperatur vom ADT7410
  float temp = readADT7410();
  if (!isnan(temp)) {
    Serial.print("Temperatur: ");
    Serial.print(temp);
    Serial.println(" °C");
  } else {
    Serial.println("Fehler beim Lesen der Temperatur!");
  }

  Serial.println("-----------------------");
  delay(1000);
}
