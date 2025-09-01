# Frontend Requirements

## Functional Requirements

1. **Display of Current Measurements**
   - Show current values for the following metrics:
     - Temperature  
     - Humidity  
     - Pollen load  
     - Fine dust (particulate matter)
   - Values are updated at short intervals.

   **Rationale:** Users need a quick overview of current environmental conditions to make informed decisions (e.g., close windows, avoid outdoor activities, wear a mask).

2. **Visualization of Historical Data**
   - Display time series data as line charts.
   - Select different time ranges (e.g., last hour, 24 h, week, month).
   - Compare two buildings:
     - *Old Building* (Marienstraße)
     - *New Building* (Hanns Voith Campus)

   **Rationale:** Time series charts allow users to identify trends, patterns, and differences over time and between buildings.

3. **Customizable Warning Thresholds**
   - Users can define individual thresholds (e.g., temperature, fine dust).
   - Exceeding thresholds is visually highlighted (e.g., color change, warning icon).

   **Rationale:** This enables users to tailor the app to their personal needs.

4. **Local Storage of Settings**
   - User-defined warning values and time settings are stored in the database.
   - These are automatically loaded when the application is reopened.

   **Rationale:** This allows for easy personalization without requiring a user account or authentication.

5. **Error Messages for System Issues**
   - User-friendly display for:
     - Application unavailability (e.g., network error, backend not available)
     - Errors loading current data
   - Clear indications of the cause and possible solutions.

   **Rationale:** Transparent error communication increases user trust and reduces frustration with technical problems.

---

## Technical Requirements

- **Data Visualization:**  
  Use **Recharts** (preferred over Chart.js) for line chart visualization.

  **Rationale:**
  - Recharts is natively developed for React and offers a declarative syntax.
  - Supports dynamic updates and comparative displays.

- **Styling:**  
  Use **Tailwind CSS** for layout and design.

  **Rationale:**
  - Promotes consistent, responsive UI design.
  - Reduces CSS management complexity and avoids naming conflicts.

- **Authentication:**  
  **No authentication will be implemented.**

  **Rationale:**
  - The application only displays public, non-personal environmental data.
  - Users do not store security-relevant or personal information.
  - Settings are saved but are not relevant across devices.
  - Authentication would add unnecessary complexity (e.g., login system, token handling) without added value for the application.

- **Performance:**
  - Fast loading times and smooth switching between time ranges and buildings.

---

## Wireframe

![Home](./images/frontend-home.jpg)

![Warnings](./images/frontend-warnings.jpg)
