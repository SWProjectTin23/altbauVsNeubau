FROM python:3.11-slim

WORKDIR /app

COPY sensor-exporter/exporter.py /app/
COPY sensor-exporter/requirements.txt /app/
COPY backend/common /app/common/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "exporter.py"]