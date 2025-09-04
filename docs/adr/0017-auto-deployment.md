# Automated Deployment via GitHub CI/CD

**Date:** 2025-09-02  

## Status

Accepted  

## Context

As described in [ADR 0010: Migration to Own Server Infrastructure Instead of AICON Server](./0010-migration-to-own-server-infrastructure.md), we moved our hosting from university-managed servers to our own dedicated infrastructure. This change provided us with full control, improved accessibility, and enhanced reliability.

## Decision

We implemented an **automated deployment process** using a GitHub Actions CI/CD pipeline:

* On every push to the main branch, the pipeline builds and tests the application.
* Successful builds are deployed to our own server infrastructure using Docker and Docker Compose.
* The pipeline ensures that the servers always run the latest tested version of the application in a reproducible environment.

## Consequences

* **Consistent Deployment:** The GitHub CI/CD pipeline guarantees reproducible and up-to-date deployments.
* **Full Control:** We manage the deployment infrastructure and process independently.
* **Operational Responsibility:** Maintenance, updates, and security of the servers remain our responsibility.
