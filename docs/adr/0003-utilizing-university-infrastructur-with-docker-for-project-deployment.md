# Utilizing University Infrastructur with Docker for Project Deployment

Date: 2025-07-15

## Status

Expired

## Context

Our project consists of multiple components that require a consistent and reproducible environment for presentations and demonstrations. Currently, manually deploying the project on presentation machines is error-prone and time-consuming. We need a solution that ensures the project environment is always identical and easily accessible. The university offers a General Informatics server that could serve as a central deployment platform.

### Alternatives Considered

We evaluated several approaches for project deployment:

Manual installation on presentation machines: This approach is highly error-prone, inefficient, and inconsistent. Each presentation would require re-configuration, potentially leading to version conflicts and "it works on my machine" issues. This was rejected due to high maintenance overhead and unreliability.

Direct deployment of application files on the university server without containerization: This would require direct installation of application dependencies on the server. It's prone to conflicts with other applications on the server and makes it difficult to ensure a consistent runtime environment that matches the development environment. This was rejected as it doesn't sufficiently guarantee reproducibility and isolation.

Using external cloud services for hosting: While cloud services offer high availability, they would incur additional costs and potentially complicate data transfer and adherence to university internal policies. This was rejected as the internal university infrastructure is sufficient for our purposes and more cost-effective.

## Decision

We will leverage Docker to deploy our project on the university's General Informatics server. The application and its dependencies will be encapsulated in Docker containers, ensuring an isolated and reproducible runtime environment.

The deployment process will involve building Docker images and then deploying them to the university server. This will enable us to present the project at any time in a defined state and ensure that we always access the same, tested version.

## Consequences

* **Consistent and Reproducible Environments:** Docker ensures that the runtime environment on the server is identical to the development environment, eliminating "it works on my machine" problems.

* **Simplified Deployment:** Once Docker images are built, deploying them to the server is a straightforward process, minimizing manual configuration steps.

* **Efficient Resource Utilization:** Utilizing existing university infrastructure avoids the need to procure and maintain our own servers, saving costs and effort.

* **Centralized Availability:** The project will be centrally available on the university server at all times, simplifying access for presentations and team members.

* **Dependency on University Resources:** The availability and maintenance of the university server will impact the accessibility and reliability of our deployment.

* **Required Docker Knowledge:** The team will need basic knowledge of creating and managing Docker containers.