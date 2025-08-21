# Altbau vs Neubau – Frontend Documentation

## Overview

This React frontend visualizes sensor data and warning thresholds for the "Altbau vs Neubau" project. It provides a dashboard for live and historical metrics, as well as a page for viewing and managing warning values.

## Structure

- **Main Entry:** `src/App.js`
- **Pages:**
  - `src/pages/Dashboard.jsx` – Main dashboard with charts and metric selection
  - `src/pages/Warnings.jsx` – Warning thresholds overview and management
- **Assets:** Images and static files in `src/assets/`
- **Styling:** Global styles in `src/App.css` and component-specific classes

## Routing

Uses [react-router-dom](https://reactrouter.com/) for navigation:

| Path            | Component   | Description                  |
|-----------------|------------|------------------------------|
| `/`             | Dashboard  | Main dashboard view          |
| `/warnwerte`    | Warnings   | Warning values management    |

## Main Features

- **Background Blur:** Uses a campus photo as a blurred background for visual appeal.
- **Header:** Displays project title and logo.
- **Dashboard:** Interactive charts for metrics (temperature, humidity, pollen, particulate matter) with interval selection and per-chart line toggling.
- **Warnings:** Shows current warning thresholds.
- **Footer:** Contains copyright

## Customization

- **Logo:** Replace `/logo512.png` for your own branding.
- **Background Image:** Change `src/assets/Aussenaufnahme_Marienstrasse_Hanns-Voith-Campus_Schloss_Fotograf_Oliver_Vogel_Startseite.jpg` for a different background.
- **Colors & Styles:** Adjust `src/App.css` and component styles as needed.

## Backend-related Documentation
### 1. Sensor Data Validation: [sensor-data-validation.md](sensor-data-validation.md)
### 2. Logging specification: [logging.md](logging.md)
### 3. Exception handling: [exceptions.md](exceptions.md)