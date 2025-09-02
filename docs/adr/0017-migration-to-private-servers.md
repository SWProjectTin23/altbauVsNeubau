# Migration to Private Servers with GitHub CI/CD Pipeline for Automated Deployment

**Date:** 2025-09-02  

## Status

Accepted  

## Context

In [ADR 0003: Utilizing University Infrastructure with Docker for Project Deployment](./0003-utilizing-university-infrastructur-with-docker-for-project-deployment.md) and [ADR 0004: GitHub Actions with Self-Hosted Runner for Automated Deployment Workflow](./0004-github-actions-with-self-hosted-runner-for-automated-deployment-workflow.md), we initially decided to use the university’s General Informatics server as the central deployment platform, combined with a self-hosted GitHub Actions runner for automated deployments.  

This setup served its purpose for consistent, reproducible deployments and seamless integration with GitHub. However, it also introduced constraints:  

* **Dependency on university infrastructure:** Server availability, maintenance schedules, and access policies were beyond our direct control.  
* **Limited flexibility:** Resource allocation and administrative rights were restricted, complicating troubleshooting and scaling.  
* **Operational risks:** Issues like Docker volume permission conflicts required administrative intervention, slowing down deployment processes.  

To gain more independence and flexibility, we evaluated alternatives and decided to migrate away from university infrastructure.  

## Decision

We migrated deployment from the university’s General Informatics server to **two privately managed servers** under our direct control.  

A GitHub Actions CI/CD pipeline handles the automated deployment process:  

* On every push to the main branch, the pipeline builds and tests the application.  
* Successful builds are deployed to the private servers using Docker and Docker Compose.  
* The pipeline ensures that the servers always run the latest tested version of the application in a reproducible environment.  

This approach builds on the principles of ADR 0003 and ADR 0004 but removes the dependency on university infrastructure. Both ADRs are therefore marked as **Expired**.  

## Consequences

* **Increased Control & Flexibility:** We have full control over the servers, including permissions, scaling, and maintenance schedules.  
* **Independent Infrastructure:** No dependency on university IT policies or availability, improving reliability and autonomy.  
* **Consistent Deployment Process:** The GitHub CI/CD pipeline ensures reproducible deployments, similar to the previous setup.  
* **Operational Overhead:** Server maintenance (updates, security patches, monitoring) is now our responsibility.  
* **Costs:** Running private servers introduces additional financial and operational costs compared to using university infrastructure.  
