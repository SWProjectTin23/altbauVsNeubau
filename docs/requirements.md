# Funktionale Requirements

- **FR-01:**  
  Die Software muss alle 10 Sekunden Temperatur- und Feinstaubwerte erfassen und automatisiert an die Datenplattform senden.

- **FR-02:**  
  Alle Sensordaten müssen einen Zeitstempel und eine genaue Zuordnung zum Standort (Alt- oder Neubau) haben und in einer zentralen Datenbank gespeichert sein, um Zeitreihenvergleiche zwischen den Standorten zu ermöglichen.

- **FR-03:**  
  Warnwerte (Temperatur zu hoch, Luftqualität zu schlecht) müssen definiert und berücksichtigt werden.

- **FR-04:**  
  Die Benutzeroberfläche soll es ermöglichen, die Temperatur- und Feinstaubdaten beider Standorte grafisch darzustellen.

- **FR-05:**  
  Das System muss automatisch eine Warnung generieren, wenn gemessene Umweltwerte festgelegte Grenzwerte überschreiten.  
  Die Warnung muss im Dashboard visuell angezeigt werden und der Benutzer soll eine Push-Benachrichtigung erhalten.

---

# Nicht-Funktionale Requirements

- **NFR-01:** Das System muss sicherstellen, dass mindestens **70,00 %** der Sensordaten pro Tag erfolgreich übertragen und gespeichert werden.  
  Wenn ein Sensor für mehr als 10 Minuten keine Daten sendet, muss das System dies automatisch erfassen und protokollieren.

  ### Messmethode:
  - **Log-Analyse:**
      - Hochrechnen, wie viele Messwerte pro Sensor pro Tag erwartet werden (Soll-Werte).
      - Tatsächlich gespeicherte Werte in TimescaleDB abfragen (Ist-Werte).
      - `Verfügbarkeit = Ìst/Soll`
  - **Timeout-Überwachung:**
      - Backend protokolliert, wenn ein Sensor >10 Minuten keine Daten sendet.

- **NFR-02:** Die Weboberfläche muss eine Verfügbarkeit von mindestens **95 %** gewährleisten.  
  Fehler müssen für Nutzer durch verständliche Fehlermeldungen gekennzeichnet sein.

  ### Messmethode:
  - **Monitoring:**
    - Externes Monitoring-Tool (ggf. selbst gehostet)
  
- **NFR-03:** Die Visualisierung der Raumqualitätsdaten im Dashboard muss innerhalb von **2 Sekunden** nach Benutzeranfrage vollständig geladen werden, selbst bei gleichzeitiger Nutzung durch bis zu 20 Benutzer.

  ### Messmethode:
  - **Monitoring:**
    - Externes Monitoring-Tool (ggf. selbst gehostet)
    - Lasttest mit 20 parallelen Nutzern

- **NFR-04:** Der Quellcode des Systems muss modular aufgebaut und dokumentiert sein, sodass Änderungen an einzelnen Komponenten (z. B. Sensorprotokoll, Visualisierung) ohne Auswirkungen auf andere Teile vorgenommen werden können. Zusätzlich muss für jede Hauptkomponente mindestens ein automatisierter Komponententest vorhanden sein.

  ### Messmethode:
  - **Backend-Struktur in Flask**
      -`mqtt/` (MQTT-Handler)
      -`storage/`(DB-Zugriff)
      -`api/`(REST-Endpunkte)
      -`test/`(Unit- und Integrationstests)
  - **GitHub Actions CI/CD**
      - Automatischer Testlauf bei jedem Pull Request auf `main`

  - **Dokumentation**
      - OpenAPI-Schema für REST
      - README + kurze Entwicklerdoku
        
- **NFR-05:** Das System muss so ausgelegt sein, dass es bei Ausfall eines Sensors oder Verbindungsabbrüchen weiterhin lauffähig bleibt und automatisch einen Wiederverbindungsversuch innerhalb von **5 Sekunden** unternimmt.  
  Fehlgeschlagene Datenübertragungen dürfen nicht zum Systemabsturz führen, sondern müssen protokolliert und ggf. in einer Warteschlange zwischengespeichert werden.

  ### Messmethode:
  - **MQTT-Client in Flask**
    - Reconnect-Logik alle 5 Sekunden bei Brokerverlust
  - **System bleibt lauffähig** auch ohne alle Sensoren --> Frontend zeigt "Sensor offline"
 
- **NFR-06:** Die Software-Komponenten müssen containerisiert (z. B. mittels Docker) bereitgestellt werden, um einen einfachen Plattformwechsel (z. B. von einem lokalen Server zu einer Cloud-VM) ohne Anpassung des Codes zu ermöglichen. Zusätzlich muss das System auf mindestens zwei unterschiedlichen Betriebssystemen (z. B. Linux und Windows) erfolgreich installiert und betrieben werden können.

  ### Messmethode:
  - Docker-Setup mit:
      -`flask-backend`
      -`react-frontend`
      -`timescaledb`
  - Docker Compose für lokale Entwicklung + Deployment
  - CI/CD-Test auf Linux + Windows via Github Actions
  - Environment Variables für alle Pfade und Secrets statt Hardcoding


---
| **Systemelement**        | **Funktion**                                | **Fehlermöglichkeit**                       | **Ursache**                                | **Auswirkung**                             |
|--------------------------|---------------------------------------------|---------------------------------------------|---------------------------------------------|---------------------------------------------|
| Arduino                  | Erfassen von Sensordaten                    | Sensor liefert keine Daten                  | Sensor defekt, Kabelbruch, Stromversorgung  | Keine Daten in DB / auf Website             |
| Temperatursensor         | Messen der Temperatur                       | Temperatur wird nicht korrekt gemessen      | Sensor falsch kalibriert / beschädigt       | Falsche Anzeige auf Website                 |
| Luftqualitätssensor      | Messen der Luftqualität                     | Keine oder falsche Messwerte                | Sensor zu alt, falsch konfiguriert          | Irreführende Daten auf Website              |
| MQTT-Verbindung          | Übertragen der Daten vom Arduino zum Server | Verbindung bricht ab                        | Netzwerkausfall, Broker nicht erreichbar    | Datenverlust / keine Anzeige                |
| MQTT-Broker              | Empfang der Messdaten                       | Broker ist nicht erreichbar                 | Serverausfall                               | Daten gehen verloren, System nicht nutzbar  |
| Datenbank                | Speichern der Daten                         | Daten werden nicht gespeichert              | Datenbankserver überlastet / fehlerhaft     | Keine Historie / Anzeige auf Website        |
| Website                  | Anzeigen der Messdaten                      | Seite ist nicht verfügbar                   | Server down, DNS-Probleme, Backendfehler    | Nutzer kann Daten nicht sehen               |
| Webserver                | Hosten der Website                          | Webserver ist offline                       | Stromausfall, Hosting-Probleme              | Keine Datenanzeige                          |


---
# Qualitätsmerkmale 
- Zuverlässigkeit
- Fehlertoleranz
- Performance
