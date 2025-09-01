# Altbau vs Neubau – Frontend Documentation

## Overview

This React frontend visualizes sensor data and warning thresholds for the "Altbau vs Neubau" project. It provides a dashboard for live and historical metrics, as well as a page for viewing and managing warning values.

## Structure

- **Main Entry:** `src/App.js`
- **Pages:**
  - `src/pages/Dashboard.jsx` – Main dashboard with charts and metric selection
  - `src/pages/Warnings.jsx` – Warning thresholds overview and management
  - `src/pages/ConfirmEmail.jsx`- Page for email confirmation (Double opt in)
- **Assets:** Images and static files in `src/assets/`
- **Components:** Components for Pages in `src/components/`
- **Styling:** Global styles in `src/App.css` and component-specific classes

## Routing

Uses [react-router-dom](https://reactrouter.com/) for navigation:

| Path            | Component   | Description                  |
|-----------------|------------|------------------------------|
| `/`             | Dashboard  | Main dashboard view          |
| `/warnings`    | Warnings   | Warning values management    |
| `/confirm-email`    | ConfirmEmail   | Confirm Email for alerting   |

## Main Features

- **Header:** Displays project title and logo.
- **Dashboard:** Interactive charts for metrics (temperature, humidity, pollen, particulate matter) with interval selection and per-chart line toggling.
- **Warnings:** Show and set current warning thresholds.
- **Footer:** Contains copyright and contact-link