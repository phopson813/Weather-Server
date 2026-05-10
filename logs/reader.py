import sqlite3
import json
import os

# Paths
BASE_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(BASE_DIR, 'sensor_log_fixed.txt')
DB_FILE = os.path.join(BASE_DIR, 'newdb.db')
JSON_FILE = "/home/phopson1@isuad.indstate.edu/public_html/sensor.json"

# Connect to SQLite DB
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Create table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station TEXT,
    tempF REAL,
    tempC REAL,
    humidity REAL,
    time TEXT,
    created_at DATETIME,
    raw_line TEXT
)
""")
conn.commit()

# Read log and insert all lines
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()

        if lines:
            last_line = None
            for l in reversed(lines):
                l = l.strip()
                if l:
                    last_line = l
                    break

            if not last_line:
                exit()


            # Try parsing JSON
            try:
                data = json.loads(last_line)
                station = data.get('Station')
                tempF = data.get('TempF')
                tempC = data.get('TempC')
                humidity = data.get('Humidity')
                time_val = data.get('Time')
                created_at = time_val
            except json.JSONDecodeError:
                # Bad JSON -> store raw line only
                station = tempF = tempC = humidity = time_val = created_at = None

            try:
                c.execute("""
                    INSERT INTO readings (station, tempF, tempC, humidity, time, created_at, raw_line)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (station, tempF, tempC, humidity, time_val, created_at, last_line))
                conn.commit()

                if 'data' in locals() and data:
                    with open(JSON_FILE, 'w') as f_json:
                        json.dump(data, f_json, indent=2)


            except Exception as e:
                print(f"Error inserting line: {e}")
        # Write last reading + max temp to sensor.json
            try:
                data = json.loads(last_line)
                c.execute("SELECT tempF, time FROM readings WHERE tempF = (SELECT MAX(tempF) FROM readings) LIMIT 1")
                row_max = c.fetchone()
                if row_max:
                    data["MaxTempF"] = row_max[0]
                    data["MaxTempTime"] = row_max[1]

                c.execute("SELECT tempF, time FROM readings WHERE tempF = (SELECT MIN(tempF) FROM readings) LIMIT 1")
                row_min = c.fetchone()
                if row_min:
                    data["MinTempF"] = row_min[0]
                    data["MinTempTime"] = row_min[1]

                c.execute("SELECT humidity, time FROM readings WHERE humidity = (SELECT MIN(humidity) FROM readings) LIMIT 1")
                row_HUMmin = c.fetchone()
                if row_min:
                    data["MinHumidity"] = row_HUMmin[0]
                    data["MinHumidityTime"] = row_HUMmin[1]
                c.execute("SELECT humidity, time FROM readings WHERE humidity = (SELECT Max(humidity) FROM readings) LIMIT 1")
                row_HUMmax = c.fetchone()
                if row_min:
                    data["MaxHumidity"] = row_HUMmax[0]
                    data["MaxHumidityTime"] = row_HUMmax[1]

                with open(JSON_FILE, 'w') as f_json:
                    json.dump(data, f_json, indent=2)
            except json.JSONDecodeError:
                pass




conn.close()