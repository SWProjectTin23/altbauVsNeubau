
# Frontend JMeter Load & Smoke Test Guide

This guide explains how to run the JMeter performance tests for the frontend and backend API.  
It covers **local execution** using Docker and **CI/CD automation** via GitHub Actions.

---

## 1. Prerequisites

Before running the tests locally, ensure you have:

- **Docker** installed and running ([Download](https://www.docker.com/get-started))
- **Docker Compose** installed (usually comes with Docker Desktop)
- Bash shell (Linux, macOS, or Git Bash on Windows)
- Application stack (frontend, backend, DB) running

---

## 2. Test Files Overview

| File | Purpose |
|------|---------|
| `.env` | Environment variables (target URLs, number of users, ramp-up time, etc.) |
| `run-jmeter.sh` | Bash script that executes the JMeter test inside Docker |
| `plan.jmx` | The JMeter test plan (defines test steps, requests, and data collection) |
| `results/` | Folder where test results and HTML reports are saved |
| `frontend-test.yml` | Docker Compose / GitHub Actions configuration for automated tests |

---

## 3. Local Execution

### Step 1 — Configure `.env`
Edit `.env` to match your environment:

```env
TARGET_URL=http://altbau_vs_neubau_frontend       # Frontend service URL
API_BASE=http://altbau_vs_neubau_api:5000/api     # API base URL
USERS=15                                          # Number of virtual users
RAMP=15                                           # Ramp-up time in seconds
COMPOSE_NETWORK=altbauvsneubau_pg-network         # Docker network (optional)
````

### Step 2 — Start Your Application

If using Docker Compose:

```bash
docker compose up -d
```

Make sure the frontend and backend are reachable:

```bash
curl http://localhost:3000/
curl http://localhost:5001/health
```

### Step 3 — Run the Test

From the `frontend-loadtest` directory:

```bash
chmod +x run-jmeter.sh
./run-jmeter.sh
```

This will:

* Clean previous results
* Detect networking configuration
* Run JMeter in non-GUI mode inside Docker
* Save results to `results/` and generate an HTML report

### Step 4 — View the Results

Open the generated report in your browser:

```bash
open results/report/index.html     # macOS
xdg-open results/report/index.html # Linux
```

---

## 4. CI/CD Execution (GitHub Actions)

This project includes a GitHub Actions workflow (`frontend-test.yml`) that runs the JMeter smoke test on:

* Pull requests to the `main` branch
* Manual trigger via **Actions → Run workflow**

### Workflow Steps

1. Checkout repository code
2. Start app stack in Docker Compose
3. Normalize line endings to avoid CRLF issues
4. Run JMeter smoke test
5. Upload artifacts (HTML report, JTL results, logs)
6. Evaluate SLOs:

   * Initial Page TTLB p95 < 2000ms
   * Click intervals p95 < 600ms
   * Fail build if thresholds are exceeded
7. Show service logs if a failure occurs
8. Tear down the Docker stack

---

## 5. Key Variables

| Variable          | Description                                       |
| ----------------- | ------------------------------------------------- |
| `USERS`           | Number of concurrent virtual users                |
| `RAMP`            | Ramp-up time in seconds (time to start all users) |
| `TARGET_URL`      | Base URL of frontend                              |
| `API_BASE`        | Base URL of API                                   |
| `COMPOSE_NETWORK` | Docker network name (optional)                    |

---

## 6. Troubleshooting

**Problem:** `.env: line 1: $'\r': command not found`
**Solution:** Convert `.env` to LF endings:

```bash
sed -i 's/\r$//' .env
```

**Problem:** No `index.html` report generated
**Solution:**

* Ensure `results/report/` is empty before running
* Remove duplicate JTL writing from `plan.jmx` if using `-l` in CLI

**Problem:** Frontend/Backend not reachable
**Solution:** Start services with:

```bash
docker compose up -d
```

and verify with `curl`.

---

## 7. Example Command Summary

```bash
# Start app
docker compose up -d

# Run test
cd frontend-loadtest
./run-jmeter.sh

# View report
xdg-open results/report/index.html
```

---

## 8. SLO Evaluation Logic

The workflow checks **95th percentile response times** from the JMeter results (`results.jtl`):

| Test Label           | Threshold   |
| -------------------- | ----------- |
| Initial Page TTLB    | `< 2000 ms` |
| Click 3h, 1d, 1w, 1m | `< 600 ms`  |

If any p95 latency exceeds its threshold, the build fails.

---

**Author’s Note:**
This setup allows you to run quick **smoke tests** during development and automated **performance checks** in CI/CD.
By adjusting `USERS` and `RAMP` in `.env`, you can scale tests from light load to stress conditions.


