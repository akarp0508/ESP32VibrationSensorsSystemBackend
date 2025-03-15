import random
from influxdb import InfluxDBClient
from datetime import datetime

host = "localhost"
port = 8086
username = "admin"
password = "adminpassword"
database = "vibration_sensor"

client = InfluxDBClient(host=host, port=port, username=username, password=password, database=database)


def fetch_data(selected_value, start_datetime, end_datetime, sensor_id):
    """Fetch data from InfluxDB along with timestamps, making the first timestamp zero."""
    start = int(start_datetime.timestamp())
    end = int(end_datetime.timestamp())
    query = f"""
    SELECT "{selected_value}" FROM "mqtt_consumer"
    WHERE time >= {start}000000000 AND time <= {end}000000000 AND sensor_id = '{sensor_id}'
    ORDER BY time ASC
    """

    print(query)
    result = client.query(query)
    
    # Wyciągniecię punktów
    points = result.get_points()
    
    # Przygotowanie pustych list
    timestamps = []
    data = []
    
    # Pierszy timestamp, aby reszta mogła być zależna od niego
    first_timestamp = None

    for point in points:
        timestamp = datetime.strptime(point['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        if first_timestamp is None:
            first_timestamp = timestamp
        
        relative_time = (timestamp - first_timestamp).total_seconds()
        timestamps.append(relative_time)
        data.append(point[selected_value])
    
    return timestamps, data


def get_sensor_ids():
    """Return a list of new options for the editable combobox."""
    query = """
    SHOW TAG VALUES FROM "mqtt_consumer" WITH KEY = "sensor_id"
    """

    result = client.query(query)

    points = result.get_points();

    sensors = []

    for point in points:
        sensors.append(point['value'])

    return sensors
