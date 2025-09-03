# Frontend JMeter Smoke Test Workflow

## Purpose

This workflow runs JMeter-based smoke tests against the frontend to ensure basic performance and availability. It checks initial page load times and interval click response times against defined Service Level Objectives (SLOs).

## Triggers

- On pull requests targeting the `main` branch
- Manual execution via the Actions tab (`workflow_dispatch`)

## Steps

1. **Checkout Repository:**  
   Retrieves the latest code from the repository.

2. **Set up Docker Buildx:**  
   Prepares the runner for advanced Docker builds.

3. **Start App Stack:**  
   Uses Docker Compose to start backend, frontend, and database services.

4. **Normalize Line Endings:**  
   Ensures scripts use LF endings to avoid CI issues.

5. **Reachability Checks:**  
   Verifies that the frontend and backend are reachable via HTTP.

6. **Run JMeter Smoke Test:**  
   Executes the JMeter test script in the `frontend-loadtest` directory.

7. **Upload JMeter Artifacts:**  
   Stores JMeter HTML reports and raw results as workflow artifacts.

8. **Evaluate SLOs:**  
   Checks if the 95th percentile latency for page loads and interval clicks meets the defined thresholds. Fails the build if not.

9. **Show Service Logs:**  
   Displays logs from backend, frontend, and database containers for debugging.

10. **Tear Down:**  
    Stops and removes all Docker Compose services and volumes.

## Environment Variables

- SLO thresholds for performance checks
- Docker Compose secrets for database and MQTT configuration
- JMeter test runner variables

## Notes

- All steps run on Ubuntu GitHub-hosted runners.
- Artifacts are available for download after each run.
- Performance failures will fail the build.