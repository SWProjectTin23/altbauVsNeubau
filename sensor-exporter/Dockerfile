# Builder
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /build

COPY sensor-exporter/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime
FROM python:3.11-slim as runtime

# Update in order to minimize attack vectors
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Since UID 500 - 1000 taken for new users => 1001 for the appuser (best practice as seen online => )
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1001 appuser

WORKDIR /app

# Since no project management tool was used, the packages are installed in the default python user folder which is /home/<user>/.local 
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local

COPY --chown=appuser:appgroup sensor-exporter/exporter.py /app/
COPY --chown=appuser:appgroup ../backend/common /app/backend/common/

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

CMD ["python", "-u", "exporter.py"]