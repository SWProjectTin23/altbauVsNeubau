# Frontend JMeter Smoke Test Guide

This guide explains how to run the JMeter **smoke test** for the frontend.  
It focuses on validating the **Initial Page TTLB (Time-To-Last-Byte)** against an SLO threshold.

---

## 1. Test Files Overview

| File | Purpose |
|------|---------|
| `.env` | Environment variables (target URLs, number of users, ramp-up time, etc.) |
| `run-jmeter.sh` | Bash script that executes the JMeter test inside Docker |
| `plan.jmx` | The JMeter test plan (defines test steps, requests, and data collection) |
| `results/` | Folder where test results and HTML reports are saved |
| `frontend-test.yml` | GitHub Actions workflow for automated smoke test |

---

## 2. Local Execution

### Step 1 — Configure `.env`
Default values:

```env
TARGET_URL=http://hrschmllr.de:3000     # Frontend service URL
API_BASE=http://hrschmllr.de/api        # API base URL
USERS=20                                # Number of virtual users
RAMP=30                                 # Ramp-up time in seconds
COMPOSE_NETWORK=frontend_pg-network     # Docker network (optional)
```

### Step 2 — Start Your Application

```bash
docker compose up -d
```

Check reachability:

```bash
curl http://hrschmllr.de:3000/
curl http://hrschmllr.de/api/health
```

### Step 3 — Run the Test

```bash
cd frontend-loadtest
chmod +x run-jmeter.sh
./run-jmeter.sh
```

This will:

* Clean previous results  
* Run JMeter inside Docker in non-GUI mode  
* Save results to `results/` and generate an HTML report  

### Step 4 — View Results

```bash
xdg-open results/report/index.html
```

---

## 3. CI/CD Execution (GitHub Actions)

The GitHub Actions workflow runs the smoke test:

* On pull requests to `main`  
* On manual trigger via **Actions → Run workflow**  

### Workflow Steps

1. Checkout repository code  
2. Start app stack in Docker Compose  
3. Normalize line endings  
4. Run JMeter smoke test  
5. Upload results (HTML report, JTL, logs)  
6. Evaluate **TTLB SLO only**  
7. Show logs on failure  
8. Tear down the Docker stack  

---

## 4. Key Variables

| Variable          | Description                                       | Example Value             |
| ----------------- | ------------------------------------------------- | ------------------------- |
| `USERS`           | Number of concurrent virtual users                | `20`                      |
| `RAMP`            | Ramp-up time in seconds                           | `30`                      |
| `TARGET_URL`      | Base URL of frontend                              | `http://hrschmllr.de:3000`|
| `API_BASE`        | Base URL of API                                   | `http://hrschmllr.de/api` |
| `COMPOSE_NETWORK` | Docker network name (optional)                    | `pg-network`     |

---

## 5. SLO Evaluation Logic

The workflow checks the **95th percentile of Initial Page TTLB**:  

| Test Label        | Threshold   |
| ----------------- | ----------- |
| Initial Page TTLB | `< 2000 ms` |

If the measured p95 latency exceeds the threshold, the build fails.

---

## 6. GitHub Actions Workflow


This project includes an automated **smoke test** that runs on every **pull request**.  
The test checks the **Initial Page TTLB (Time-To-Last-Byte)** and enforces a strict **Service Level Objective**:

- **p95 latency must stay below 2000 ms (2 seconds)**

If the threshold is exceeded, the workflow fails and the pull request cannot be merged until performance is improved.
---
