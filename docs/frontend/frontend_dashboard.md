# Dashboard Page Documentation

## Overview

The **Dashboard Page** is the central hub of the "Altbau vs Neubau" frontend.  
It provides users with a clear, interactive overview of all relevant sensor data, including current values and historical trends for both the "Altbau" and "Neubau" buildings.  
The dashboard is designed for quick status checks, in-depth analysis, and direct access to warning threshold management.

---

## Main Features

### 1. **Current Values Table**
- Displays the latest sensor readings for each metric (Temperature, Humidity, Pollen, Particulate Matter) for both buildings.
- Highlights values that exceed warning or critical thresholds using color-coded cells.
- Shows the timestamp of the most recent measurement per building.
- If a sensor is unavailable, the table indicates this clearly.

### 2. **Interactive Charts**
- For each metric, a line chart visualizes historical data for both buildings over a selectable time interval.
- Users can toggle the visibility of each building's data series via the legend.
- Charts automatically insert gaps if data is missing, making outages or sensor failures visible.
- Tooltips provide precise values and timestamps on hover.
- Clicking a chart opens a modal with a larger, more detailed view.

### 3. **Interval Selection**
- Users can choose the time range for historical data (e.g., 30 minutes, 1 hour, 1 day, 1 week, 1 month).
- Interval selection updates all charts and data accordingly.

### 4. **Warning Thresholds Integration**
- Thresholds are fetched from the backend and used to color-code both the current values and chart lines.
- A button provides direct navigation to the warning management page.

### 5. **Error Handling & Feedback**
- If data cannot be loaded, the dashboard displays clear error messages.
- Loading states are shown while data is being fetched.

---

## Technical Details

- **Component Structure:**  
  - `Dashboard.jsx` orchestrates data fetching, state management, and layout.
  - `CurrentValuesTable` renders the latest sensor values.
  - `ChartCard` and `ChartModal` handle chart rendering and modal display.
  - Utility functions in `dashboardUtils.js` manage data mapping, interval calculation, and formatting.
  - `IntervalButtons`, `CustomLegend`, and `CustomTooltip` provide interactive UI elements.

- **Data Flow:**  
  - Fetches current and historical sensor data from the backend API.
  - Fetches warning thresholds and applies them for visual feedback.
  - Sends alert mail requests when current values exceed thresholds.

- **Styling:**  
  - Uses global and page-specific CSS for layout, responsiveness, and color coding.
  - Charts are rendered with [Recharts](https://recharts.org/).

---

## User Experience

- **Quick Status:**  
  Instantly see if any metric is in a warning or critical state.
- **Analysis:**  
  Explore historical trends and compare buildings side-by-side.
- **Action:**  
  Navigate to warning management to adjust thresholds as needed.

---

## Summary

The Dashboard Page is designed to be the main entry point for users, combining real-time monitoring, historical analysis, and actionable insights in a single, intuitive interface.  
It supports the overall goal of the project: making building sensor data transparent, actionable, and easy to manage.

For more details on the frontend structure, see [frontend.md](./frontend.md).