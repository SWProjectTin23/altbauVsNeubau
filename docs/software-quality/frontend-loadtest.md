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
- If the threshold is exceeded, the workflow fails and the pull request cannot be merged until performance is improved.
---


## Our Test Statistics

The load test was executed with **20 virtual users** and a **30-second ramp-up**.  
The configured **total test duration was 180 seconds (3 minutes)**.
Given an observed per-endpoint throughput of ~**6.9 req/s**, this yields about  
**1,200 requests per endpoint** (≈ 1,233 samples). The overall scenario produced **8,646 requests**.

| Label                                | Samples | Errors | Error % | Avg (ms) | Min | Max  | p50  | p90   | p95   | p99    | Throughput/s | KB/sec | Avg. Bytes |
|--------------------------------------|---------|--------|---------|----------|-----|------|------|-------|-------|--------|--------------|--------|------------|
| **Total**                            | 8646    | 0      | 0.00%   | 148.24   | 0   | 2581 | 58.0 | 467.0 | 526.0 | 686.53 | 48.31        | 8039.51| 11.95      |
| GET http://hrschmllr.de:3000/        | 1233    | 0      | 0.00%   | 516.49   | 354 | 1765 | 494.0| 600.6 | 708.2 | 899.98 | 6.89         | 4006.76| 5.95       |
| GET http://hrschmllr.de:3000/-0      | 1233    | 0      | 0.00%   | 45.91    | 26  | 388  | 40.0 | 61.0  | 67.3  | 149.64 | 6.91         | 7.44   | 0.82       |
| GET http://hrschmllr.de:3000/-1      | 1233    | 0      | 0.00%   | 75.56    | 29  | 414  | 71.0 | 105.0 | 112.0 | 128.66 | 6.91         | 105.64 | 0.92       |
| GET http://hrschmllr.de:3000/-2      | 1233    | 0      | 0.00%   | 52.24    | 29  | 568  | 43.0 | 67.0  | 84.6  | 222.28 | 6.91         | 7.28   | 1.09       |
| GET http://hrschmllr.de:3000/-3      | 1233    | 0      | 0.00%   | 46.53    | 28  | 319  | 42.0 | 64.0  | 70.0  | 102.96 | 6.94         | 7.79   | 1.13       |
| GET http://hrschmllr.de:3000/-4      | 1233    | 0      | 0.00%   | 247.65   | 159 | 1153 | 235.0| 298.0 | 329.3 | 538.28 | 6.93         | 3849.78| 1.00       |
| GET http://hrschmllr.de:3000/-5      | 1233    | 0      | 0.00%   | 42.12    | 27  | 155  | 38.0 | 58.0  | 62.0  | 90.98  | 6.94         | 53.90  | 1.02       |
| **TTLB Dashboard**                   | 1240    | 0      | 0.00%   | 2004.27  | 0   | 3298 | 2008.5| 2435.0| 2498.9| 2717.26| 6.87         | 3973.04| 5.90       |
