from influxdb import InfluxDBClient
from datetime import datetime

class InfluxDBDataProvider:
    def __init__(self, host, port, username=None, password=None, database=None):
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.database = "vibration_sensor"
        
        # Inicjalizacja influxDB
        self.client = InfluxDBClient(
            host=self.host, 
            port=self.port, 
            username=self.username, 
            password=self.password, 
            database=self.database
        )
        result = self.client.query("")

    def fetch_data(self, selected_value, start_datetime, end_datetime, sensor_id):
        start = int(start_datetime.timestamp())
        end = int(end_datetime.timestamp())

        # Utworzenie zapytania
        query = f"""
        SELECT "{selected_value}" FROM "sensor_data"
        WHERE time >= {start}000000000 AND time <= {end}000000000 AND sensor_id = '{sensor_id}'
        ORDER BY time ASC
        """
        
        print(f"Executing query: {query}")
        result = self.client.query(query)
        
        points = result.get_points()
        
        timestamps = []
        data = []

        for point in points:
            timestamp = parse_iso_timestamp(point['time'])
            timestamps.append(timestamp)
            data.append(point[selected_value])
        
        return timestamps, data

    def get_sensor_ids(self):
        query = """
        SHOW TAG VALUES FROM "sensor_data" WITH KEY = "sensor_id"
        """
        
        result = self.client.query(query)
        
        points = result.get_points()
        sensors = [point['value'] for point in points]
        
        return sensors

def parse_iso_timestamp(time_string):
    # If there are milliseconds, use the full format; otherwise, use the shorter one
    format_str = "%Y-%m-%dT%H:%M:%S.%fZ" if "." in time_string else "%Y-%m-%dT%H:%M:%SZ"
    return datetime.strptime(time_string, format_str)