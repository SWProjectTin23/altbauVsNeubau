# Warnings / Thresholds Page Documentation

## Overview

The **Warnings Page** (also called the Thresholds Page) is the central interface for managing alert thresholds and notification settings in the "Altbau vs Neubau" frontend.  
It allows users to view, adjust, and save warning and critical limits for all monitored metrics (Temperature, Humidity, Pollen, Particulate Matter) and to configure the alert email address for notifications.

---

## Main Features

### 1. **Threshold Management Form**
- Displays all relevant metrics with their current warning ("yellow") and critical ("red") thresholds.
- Each metric (e.g., Temperature, Humidity) shows four editable fields:
  - Red Low: Critical lower limit
  - Yellow Low: Warning lower limit
  - Yellow High: Warning upper limit
  - Red High: Critical upper limit
- Values can be adjusted using input fields with increment/decrement buttons for convenience.
- Validation ensures logical consistency (e.g., red low < yellow low < yellow high < red high).

### 2. **Alert Email Configuration**
- Users can enter or update the email address to receive alert notifications.
- Implements double-opt-in: When a new email is entered, a confirmation mail is sent and alerts are only sent to confirmed addresses.
- The page provides clear feedback if confirmation is required.

### 3. **Form State & Feedback**
- The form tracks unsaved changes ("dirty" state) and disables navigation until changes are saved or discarded.
- Error messages are shown for invalid input, failed saves, or unsaved changes.
- Informational messages guide the user through confirmation steps and successful saves.
- Loading indicators are displayed while thresholds or email settings are being fetched.

### 4. **Navigation**
- Includes a button to return to the Dashboard, which is only enabled when there are no unsaved changes.

---

## Technical Details

- **Component Structure:**  
  - `Warnings.jsx` manages data fetching, state, validation, and save logic.
  - `WarningsForm.jsx` renders the form and handles user input.
  - `WarningCard.jsx` displays threshold fields for each metric.
  - `NumberInputWithButtons.jsx` provides enhanced input controls.
  - Utility functions in `warningsUtils.jsx` handle mapping, validation, and formatting.
  - `ErrorMessage.jsx` and loading components provide user feedback.

- **Data Flow:**  
  - Fetches current thresholds and alert email from the backend API on load.
  - Maps API data to UI format and vice versa for editing and saving.
  - Validates input before saving; only sends confirmation mail if the email address has changed.
  - Saves thresholds and email settings via API calls.

- **Styling:**  
  - Uses global and page-specific CSS for layout, responsive design, and color coding.
  - Error and info messages are visually distinct for clarity.

---

## User Experience

- **Intuitive Editing:**  
  Users can quickly adjust thresholds with clear labels and input controls.
- **Safe Changes:**  
  Unsaved changes are tracked, preventing accidental navigation.
- **Guided Alerts Setup:**  
  The email confirmation process is transparent and user-friendly.
- **Immediate Feedback:**  
  Errors and info messages keep users informed at every step.

---

## Summary

The Warnings / Thresholds Page empowers users to customize alerting behavior and notification settings, ensuring the system matches their needs and preferences.  
It is designed for clarity, safety, and ease of use, supporting the project's goal of actionable, user-driven building monitoring.

For more details on the frontend structure, see [frontend.md](./frontend.md).