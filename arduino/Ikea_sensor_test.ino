void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial1.begin(9600);  // RX = Pin 13 auf MKR WiFi 1010
  Serial.println("⏳ Warte auf Daten vom Vindriktning-Sensor...");
}

void loop() {
  static uint8_t buffer[20];
  static uint8_t index = 0;

  while (Serial1.available()) {
    uint8_t b = Serial1.read();

    Serial.print("Byte ");
    Serial.print(index);
    Serial.print(": 0x");
    if (b < 0x10) Serial.print("0");  // führende Null
    Serial.println(b, HEX);

    buffer[index++] = b;

    // Wenn wir 20 Bytes haben, prüfen wir das Paket
    if (index == 20) {
      Serial.println("--- Paket vollständig ---");

      // Richtige Prüfsumme prüfen:
uint8_t sum = 0;
for (int i = 0; i < 20; i++) {
  sum += buffer[i];
}
if ((sum & 0xFF) == 0) {
  Serial.println("Paket OK – Daten korrekt!");
} else {
  Serial.println("Prüfsummenfehler – Paket ungültig!");
}

// Richtige PM-Werte:
uint16_t pm25 = (buffer[5] << 8) | buffer[6];
uint16_t pm10 = (buffer[9] << 8) | buffer[10];
Serial.print("🌫️  PM2.5 = ");
Serial.print(pm25);
Serial.print(" µg/m³ | PM10 = ");
Serial.print(pm10);
Serial.println(" µg/m³");


      Serial.println("─────────────────────────────");
      index = 0;  // zurücksetzen
    }
  }
}