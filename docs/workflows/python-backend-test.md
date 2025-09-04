# Python Backend Test Workflow

## Purpose

This workflow runs automated tests for the Python backend using pytest and generates a coverage report.

## Triggers

- On pull requests targeting the `main` branch

## Steps

1. **Checkout Repository:**  
   Retrieves the latest code.

2. **Setup Python:**  
   Installs the specified Python version (e.g., 3.13).

3. **Export Environment Variables:**  
   Loads secrets for database and MQTT configuration into the environment.

4. **Install Dependencies:**  
   Installs Python dependencies from `backend/requirements.txt`.

5. **Debug Directory Structure:**  
   Prints the current directory and lists files for debugging.

6. **Set PYTHONPATH:**  
   Ensures the backend code is discoverable by pytest.

7. **Run Tests with Coverage:**  
   Executes pytest, fails on the first error, and generates a coverage report.

8. **Upload Coverage Report:**  
   Stores the HTML coverage report as a workflow artifact.

## Notes

- Coverage reports are available for download after each run.
- All steps run on Ubuntu GitHub-hosted runners.