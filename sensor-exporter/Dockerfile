FROM python:3.11-slim

WORKDIR /app

COPY sensor-exporter/exporter.py /app/
COPY sensor-exporter/requirements.txt /app/
RUN mkdir -p /app/backend
COPY backend/common /app/backend/common/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app

CMD ["python", "-u", "exporter.py"]