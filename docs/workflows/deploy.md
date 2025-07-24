# CD Workflow (Continuous Deployment)

## Docker Compose Deployment

**Purpose:**
This workflow automates the deployment of your Docker Compose application to the designated server using a self-hosted runner. It ensures that the latest version of your application is always running on the server, maintaining consistency and reliability.

**Triggers:**
* **Push to `main` branch:** Automatically deploys the latest code whenever changes are pushed to `main`.

**Runner:**
* **Self-hosted runner:** The workflow executes on a self-hosted runner, located on your target server. This allows direct interaction with Docker and the host file system for efficient deployments.

---

## Workflow Steps Explained

1.  **Checkout Repository:** Fetches the latest code from your GitHub repository onto the self-hosted runner's workspace. This ensures the runner has access to your `docker-compose.yml` and application files.
2.  **Stop and remove existing Docker Compose setup:** This crucial step gracefully shuts down any previously running Docker Compose services defined in your `docker-compose.yml` and removes their associated containers, networks, and orphan volumes. This ensures a clean slate for the new deployment and prevents conflicts. The `|| true` ensures the step doesn't fail if no services are currently running.
3.  **Pull latest Docker images:** Pulls the newest versions of all Docker images specified in your `docker-compose.yml` from their respective registries (e.g., Docker Hub). This guarantees that your deployment uses the most up-to-date service components.
4.  **Start Docker Compose setup:** Initiates your application services by running `docker compose up -d --build`.
    * `-d`: Starts the services in "detached mode" (in the background).
    * `--build`: Rebuilds Docker images from their Dockerfiles if changes are detected or if a fresh build is desired. This ensures any local code changes within your backend/frontend Dockerfiles are incorporated.

---

## Important Notes

* **Manual Execution:** This workflow is currently only triggered automatically by `push` and `pull_request` events on the `main` branch. If manual execution is desired for specific scenarios or branches, a `workflow_dispatch` trigger can be added to the workflow YAML.
* **Permissions:** Ensure the user running the self-hosted runner has the necessary permissions to execute Docker commands and manage files in its workspace. If `root`-owned files (e.g., from old Docker bind mounts) exist and cause "permission denied" errors, they must be removed by an administrator with `sudo` privileges.
* **Runner Status:** The self-hosted runner must be running and connected to GitHub (`Listening for Jobs`) for the workflow to be assigned and executed. For continuous operation, configure the runner as a `systemd` service.
* **`docker-compose.yml` location:** This workflow assumes your `docker-compose.yml` file is located in the **root directory** of your repository.