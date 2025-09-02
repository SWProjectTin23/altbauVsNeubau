# CD Workflow (Continuous Deployment)

## Docker Compose Deployment with GHCR Images

**Purpose:**  
This workflow automates the deployment of your Docker Compose application using GitHub Actions.  
It builds and pushes Docker images to the GitHub Container Registry (GHCR) and then deploys the latest version to your production server via SSH.

**Triggers:**  
* **Push to `main` branch:** Automatically builds, pushes, and deploys the latest code and Docker images whenever changes are pushed to `main`.

**Runner:**  
* **GitHub-hosted runner:** The workflow runs on GitHub's infrastructure (e.g., `ubuntu-latest`).  
  The deployment step connects to your server via SSH and executes Docker Compose commands remotely.

---

## Workflow Steps Explained

1. **Build and Push Docker Images to GHCR:**  
   On every push to `main`, GitHub Actions builds the Docker images for all services (`backend-api`, `backend-mqtt`, `frontend`, `sensor-exporter`) and pushes them to the GitHub Container Registry (GHCR).  
   See [`.github/workflows/docker-ghcr.yml`](../../.github/workflows/docker-ghcr.yml) for details.

2. **Deploy to Production Server via SSH:**  
   After building and pushing, the workflow connects to your server using SSH (`appleboy/ssh-action`).  
   It pulls the latest code and images, then starts the services using `docker compose -f docker-compose-prod.yml up -d`.

---

## Important Notes

* **Persistent Deployment:**  
  This workflow **does** deploy your application to a permanent server.  
  Make sure your server is reachable via SSH and has Docker Compose installed.

* **Secrets:**  
  The workflow uses GitHub Secrets for authentication (`SERVER_HOST`, `SERVER_USER`, `SSH_PRIVATE_KEY`, `GHCR_TOKEN`).  
  These must be configured in your repository settings.

* **`docker-compose-prod.yml` location:**  
  The workflow assumes your production Compose file is named `docker-compose-prod.yml` and is located in the project root on your server.

* **Manual Execution:**  
  The workflow is triggered automatically by pushes to the `main` branch.  
  For manual execution, add a `workflow_dispatch` trigger to the workflow YAML.

---