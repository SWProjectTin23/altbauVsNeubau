# CI Workflow

## Docker Build and Sanity Check

**Purpose:**  
Build Docker images with Docker Compose, perform a quick sanity check by starting/stopping the services.

**Triggers:**  
- Push to `main` branch  
- Pull request targeting `main`  
- Manual trigger via `workflow_dispatch`

**Steps:**  
1. Checkout code  
2. Check Docker Compose version  
3. Build Docker images (`docker compose build --no-cache --pull`)  
4. Start services briefly (`docker compose up -d`)  
5. Wait 5 seconds, then shut down (`docker compose down`)  
6. On failure, show Docker logs  

**Manual Execution:**  
Use the **Run workflow** button in the Actions tab and select the desired branch.

**Notes:**  
- To test on feature branches, add them to the `on.push.branches` list in the workflow YAML.  
- Ensure Docker Compose is installed on the runner (GitHub-hosted runners have it pre-installed).
