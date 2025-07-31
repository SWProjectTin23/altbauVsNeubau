import random
from datetime import datetime, timedelta

# Define the amount of data: 7 days, every hour
NUM_DAYS = 7
ENTRIES_PER_DAY = 24

# Contain two IDs
DEVICE_IDS = [1, 2]

def generate_entry(device_id, timestamp):
    temperature = round(random.uniform(20.0, 25.0), 2)
    humidity = round(random.uniform(30.0, 50.0), 2)
    pollen = random.randint(50, 200)
    particulate_matter = random.randint(5, 25)
    return f"({device_id}, TIMESTAMPTZ '{timestamp.isoformat()}', {temperature}, {humidity}, {pollen}, {particulate_matter})"

# Start from 21/7/2025 00:00
start_time = datetime(2025,7,21,0,0,0)
seed_entries = []

for device_id in DEVICE_IDS:
    for i in range(NUM_DAYS * ENTRIES_PER_DAY):
        ts = start_time + timedelta(hours=i)
        seed_entries.append(generate_entry(device_id, ts))

# write seed.sql
with open("seed.sql", "w") as f:
    f.write("-- Auto-generated seed data\n")
    f.write("INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, pollen, particulate_matter)\nVALUES\n")
    f.write(",\n".join(seed_entries))
    f.write(";\n")

print("seed.sql generated with mock data for 7 days x 2 devices.")
