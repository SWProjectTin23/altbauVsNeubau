# Confirm Email Page Documentation

## Overview

The **Confirm Email Page** is a dedicated interface for users to complete the double-opt-in process for alert notifications.  
When a user enters a new alert email address on the Warnings/Thresholds page, a confirmation email is sent containing a unique token.  
The user must visit the Confirm Email page (usually via a link in the email) to verify their address and activate alert notifications.

---

## Main Features

- **Token Verification:**  
  The page reads the confirmation token from the URL query parameters and sends it to the backend API for validation.
- **Status Feedback:**  
  The page displays clear feedback based on the confirmation result:
  - Pending: "Bestätige deine E-Mail-Adresse..."
  - Success: "Deine E-Mail-Adresse wurde erfolgreich bestätigt. Du erhältst nun Alerts."
  - Error: "Bestätigung fehlgeschlagen." (e.g., invalid or expired token)
- **Navigation:**  
  After confirmation, users can return to the dashboard with a single click.

---

## Technical Details

- **Component:**  
  - `src/pages/ConfirmEmail.jsx`
- **Logic:**  
  - Uses React hooks (`useEffect`, `useState`) to handle token extraction and API communication.
  - Utilizes `useSearchParams` from `react-router-dom` to read the token from the URL.
  - Calls the backend endpoint `/confirm_email` via POST with the token.
  - Displays status messages based on the API response.
- **Styling:**  
  - Uses global styles and a visually distinct info box for feedback.
  - Button for navigation back to the dashboard.

---

## User Experience

- **Guided Confirmation:**  
  Users are informed about the confirmation status at every step.
- **Error Handling:**  
  Invalid or missing tokens result in clear error messages.
- **Simple Navigation:**  
  After confirmation, users can easily return to the main dashboard.

---

## Example Workflow

1. User enters a new email address on the Warnings page.
2. System sends a confirmation email with a link:  
   `https://your-domain/confirm-email?token=abc123`
3. User clicks the link and lands on the Confirm Email page.
4. The page verifies the token and displays the result.
5. On success, alerts will be sent to the confirmed email address.

---

## Summary

The Confirm Email Page ensures that only verified email addresses receive alert notifications, improving security and user trust.  
It is a key part of the double-opt-in flow and provides a clear, user-friendly confirmation experience.

For more details on the frontend structure, see [frontend.md](./frontend.md).