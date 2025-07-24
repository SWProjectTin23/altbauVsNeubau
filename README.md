# altbauVsNeubau
DHBW Heidenheim INF2023 Semester 4

## Use Case
Dieses Projekt dient dem Vergleich der Raumluftqualität zwischen dem Altbau (Marienstraße) und dem Neubau (Hanns Voith Campus) der dualen Hochschule Heidenheim. Hierzu werden Temperatur und Luftqualität kontinuierlich in beiden Gebäuden gemessen, zentral gesammelt und ausgewertet.

### Zielsetzung
* Messung von Temperatur und Luftqualität in zwei unterschiedlichen Gebäudeteilen
* Vergleich der erfassten Daten über eine zentrale Anwendung
* Visualisierung der Daten zur Bewertung der Raumqualität

### Technischer Ablauf
1. Zwei Arduino-Boards (jeweils im Altbau und Neubau) erfassen regelmäßig Sensordaten.
2. Die Daten werden per MQTT an einen zentralen MQTT-Broker gesendet.
3. Eine Serveranwendung empfängt die Daten, validiert sie und speichert sie in einer Datenbank.
4. Eine Weboberfläche oder ein Dashboard zeigt die Messreihen grafisch im Vergleich an.

### Testabdeckung
Zur Sicherstellung der Funktionalität und Zuverlässigkeit des System soll eine gezielte Testabdeckung durch Unittests umgesetzt werden. 
Bei jedem Commit sollen die Tests automatisch über GitHub Actions gestartet werden, um die Qualität und Stabilität des Codes sicherzustellen.

## Architektur
![Systemarchitektur](./docs/architecture/ArchitekturDiagramm.svg)

## Documentation

- [Branching Strategy](docs/branchingStrategy.md)  
- [Requirements](docs/requirements.md)  
- [CI Workflows](docs/workflows/ci.md) 
- [Deploy Workflow](docs/workflows/deploy.md)
