#include <DHT.h>

// === Pins für die Sensoren ===
#define DHTPIN1 6  // Sensor 1 an D6
#define DHTPIN2 7  // Sensor 2 an D7

// === Sensortyp ===
#define DHTTYPE DHT11

// === DHT Objekte ===
DHT dht1(DHTPIN1, DHTTYPE);
DHT dht2(DHTPIN2, DHTTYPE);

// === Plausibilitätsgrenzen ===
const float MIN_TEMP = 0.0;    // °C
const float MAX_TEMP = 50.0;   // °C
const float MIN_HUM = 20.0;    // %
const float MAX_HUM = 80.0;    // %

void setup() {
  Serial.begin(9600);
  dht1.begin();
  dht2.begin();
  Serial.println("=== DHT11 Sensor Test ===");
}

void loop() {
  float t1 = dht1.readTemperature();
  float h1 = dht1.readHumidity();
  float t2 = dht2.readTemperature();
  float h2 = dht2.readHumidity();

  Serial.println("--- Messung ---");

  // Sensor 1 prüfen
  if (isnan(t1) || isnan(h1)) {
    Serial.println("Sensor 1: FEHLER beim Auslesen!");
  } else if (t1 < MIN_TEMP || t1 > MAX_TEMP || h1 < MIN_HUM || h1 > MAX_HUM) {
    Serial.print("Sensor 1: Werte unplausibel -> ");
    Serial.print(t1); Serial.print(" °C, ");
    Serial.print(h1); Serial.println(" %");
  } else {
    Serial.print("Sensor 1 -> Temp: "); Serial.print(t1); Serial.print(" °C, ");
    Serial.print("Feuchtigkeit: "); Serial.print(h1); Serial.println(" %");
  }

  // Sensor 2 prüfen
  if (isnan(t2) || isnan(h2)) {
    Serial.println("Sensor 2: FEHLER beim Auslesen!");
  } else if (t2 < MIN_TEMP || t2 > MAX_TEMP || h2 < MIN_HUM || h2 > MAX_HUM) {
    Serial.print("Sensor 2: Werte unplausibel -> ");
    Serial.print(t2); Serial.print(" °C, ");
    Serial.print(h2); Serial.println(" %");
  } else {
    Serial.print("Sensor 2 -> Temp: "); Serial.print(t2); Serial.print(" °C, ");
    Serial.print("Feuchtigkeit: "); Serial.print(h2); Serial.println(" %");
  }

  delay(2000); // DHT11 nicht schneller als alle 2 Sekunden auslesen
}
