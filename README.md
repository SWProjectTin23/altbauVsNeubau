# altbauVsNeubau
DHBW Heidenheim INF2023 Semester 4

## Use Case
This project compares indoor air quality between the old building (Marienstraße) and the new building (Hanns Voith Campus) of the Duale Hochschule Heidenheim. For this purpose, temperature and air quality are continuously measured in both buildings, centrally collected, and evaluated.

### Goal
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
![Architecture](./docs/images/ArchitecturDiagramm.svg)

---

## Setup Instructions

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed
- [Git](https://git-scm.com/) installed
- Recommended: [VS Code](https://code.visualstudio.com/) or another code editor

### Clone the Repository

```sh
git clone https://github.com/SWProjectTin23/altbauVsNeubau.git
cd altbauVsNeubau
```

### Configuration

1. Copy the example environment file and adjust secrets/credentials as needed:
   ```sh
   cp .env.example .env
   ```
   Edit `.env` to set database credentials, MQTT broker info, and SMTP settings for alerting.

2. (Optional) Review and adjust `docker-compose.yml` for your environment.

### Start the System

```sh
docker compose up -d
```

- This will start all required services:
  - TimescaleDB (PostgreSQL)
  - Backend API (Flask)
  - MQTT Handler
  - React Frontend
  - Monitoring (Prometheus, Grafana, Uptime Kuma, Loki)
  - Sensor Exporter

### Access the Application

- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Grafana Monitoring:** [http://localhost:3003](http://localhost:3003)
- **Prometheus:** [http://localhost:9090](http://localhost:9090)
- **Uptime Kuma:** [http://localhost:3002](http://localhost:3002)

### Database Initialization

- The database is initialized via `db/init.sql` and `db/availability_sensor.sql` **only on first container creation**.
- If you change the schema later, you must manually apply changes using SQL tools (e.g., `psql`).

### Running Tests

- Unit and integration tests are located in the `backend/tests/` directory.
- Run backend tests:
  ```sh
  docker compose exec backend-api pytest
  ```

---

## Documentation

- [Branching Strategy](docs/branchingStrategy.md)  
- [Requirements](docs/software-quality/requirements.md)  
- [CI Workflows](docs/workflows/ci.md)
- [Frontend Documentation](docs/frontend/frontend.md)
- [Backend Documentation](docs/backend/backend.md)
- [Database Documentation](docs/db/db.md)
- [ADR (Architecture Decision Records)](docs/adr/)

---

## Troubleshooting

- If a service does not start, check logs with:
  ```sh
  docker compose logs <service-name>
  ```
- For database schema changes, see [Database Documentation](docs/db/db.md).

---
