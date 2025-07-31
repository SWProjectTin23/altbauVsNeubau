# altbauVsNeubau
DHBW Heidenheim INF2023 Semester 4

## Use Case
This project compares indoor air quality between the old building (Marienstraße) and the new building (Hanns Voith Campus) of the Duale Hochschule Heidenheim. For this purpose, temperature and air quality are continuously measured in both buildings, centrally collected, and evaluated.

### Zielsetzung
* Measurement of temperature and air quality in two different building sections
* Comparison of collected data via a central application
* Visualization of data for assessing room quality

### Technical Workflow
1. Two Arduino boards (one in the old building and one in the new building) regularly collect sensor data.
2. The data is sent via MQTT to a central MQTT broker.
3. A server application receives the data, validates it, and stores it in a database.
4. A web interface or dashboard graphically displays the measurement series for comparison.

### Test Coverage
To ensure the functionality and reliability of the system, targeted test coverage through unit tests will be implemented.
Tests will be automatically initiated via GitHub Actions with each commit to ensure code quality and stability.

## Architecture
![Systemarchitektur](./docs/images/ArchitecturDiagramm.svg)

## Documentation

- [Branching Strategy](docs/branchingStrategy.md)  
- [Requirements](docs/requirements.md)  
- [CI Workflows](docs/workflows/ci.md) 