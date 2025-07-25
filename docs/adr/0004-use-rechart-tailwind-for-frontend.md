# 4. Use Tailwind CSS and Recharts for Styling and Charting

**Date:** 2025-07-24  
**Status:** Accepted

## Context

The web application must display real-time sensor data (e.g., temperature, humidity, pollen levels, particulate matter) and provide interactive time-series visualizations. The UI should be modern, responsive, and user-friendly. Users should also be able to:

- Compare data across different buildings (e.g., Altbau vs. Neubau).
- Define custom alert thresholds.
- Visualize historical data across configurable time ranges.
- Receive clear feedback on system errors.

Technical requirements emphasize responsive styling, seamless React integration, fast load times, and smooth transitions between views.

### Functional Requirements Recap

1. **Display of current values** (for temperature, humidity, pollen, particulate matter)
2. **Time-series visualizations** with configurable time ranges and building comparison
3. **Custom warning thresholds** and visual alerts on threshold breaches
4. **Local storage of user preferences**
5. **Clear error messages** in case of network or system issues

### Technical Requirements

- Use **Chart.js** or **Recharts** for visualizations
- Use **Tailwind CSS** for modern, responsive UI
- Ensure fast performance and smooth UI transitions

## Alternatives Considered

- **Chart.js** – Popular and powerful, but not optimized for React. The `react-chartjs-2` wrapper adds overhead and less flexibility for real-time updates.
- **Styled Components / SCSS / plain CSS** – Offers full control but requires more setup, maintenance, and consistency enforcement.
- **Recharts** – Built for React, supports declarative syntax, and is easy to integrate.
- **Tailwind CSS** – Utility-first framework that fits naturally with React’s component-driven approach and ensures consistent styling.

## Decision

We will use:

- **Tailwind CSS** for UI styling  
- **Recharts** for time-series data visualization

These tools offer seamless integration with React, promote maintainability, and support our requirements for performance, customization, and developer productivity.

## Consequences

**Tailwind CSS:**

- Enables rapid UI development using utility classes directly in JSX
- Reduces need for separate CSS files and avoids naming conflicts
- Provides responsive design patterns out-of-the-box
- Customizable through a central Tailwind configuration

**Recharts:**

- Native React integration (no wrappers needed)
- Declarative chart configuration makes logic easy to follow
- Supports dynamic updates and comparisons (e.g., by building or time range)
- Simple integration of custom highlights and threshold indicators

**General:**

- Team members must be familiar with Tailwind and Recharts (low learning curve)
- Tailwind requires minimal PostCSS configuration and tree-shaking for production
- Recharts may have limitations for highly complex or custom visualizations (D3 could be explored later if needed)

