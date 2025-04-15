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
        result = self.client.query("SHOW DATABASES")

    def fetch_data(self, selected_value, start_datetime, end_datetime, sensor_id):
        start = int(start_datetime.timestamp())
        end = int(end_datetime.timestamp())

        axis = "xyz"[selected_value % 3]
        table_name = ["sensor_data", "gyro_data"][selected_value//3]


        # Utworzenie zapytania
        query = f"""
        SELECT "{axis}" FROM "{table_name}"
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
            data.append(point[axis])
        
        return timestamps, data

    def get_sensor_ids(self):
        query = """
        SHOW TAG VALUES FROM "sensor_data" WITH KEY = "sensor_id"
        """
        
        result = self.client.query(query)
        
        points = result.get_points()
        sensors = [point['value'] for point in points]
        
        return sensors
    
    def fetch_alerts(self, page=0):
        limit = 10
        offset = page * limit

        count_query = 'SELECT COUNT(*) FROM "alert"'
        count_result = self.client.query(count_query)
        total_rows = list(count_result.get_points())[0]['count_field']
        
        max_pages = (total_rows // limit) + (1 if total_rows % limit > 0 else 0)
        print(f"Max pages: {max_pages}")

        query = f"""
        SELECT time, "field", "threshold", sensor_id FROM "alert"
        ORDER BY time DESC
        LIMIT {limit} OFFSET {offset}
        """

        print(f"Executing query: {query}")

        result = self.client.query(query)
        points = result.get_points()

        alerts = []
        fields = ["Przyspieszenie X", "Przyspieszenie Y", "Przyspieszenie Z", "Żyroskop X", "Żyroskop Y", "Żyroskop Z"]
        for point in points:
            alert = {
                "time": parse_iso_timestamp(point['time']),
                "field": fields[int(point["field"])],
                "threshold": float(point["threshold"]),
                "sensor_id": point["sensor_id"]
            }
            alerts.append(alert)

        return max_pages, alerts

def parse_iso_timestamp(time_string):
    format_str = "%Y-%m-%dT%H:%M:%S.%fZ" if "." in time_string else "%Y-%m-%dT%H:%M:%SZ"
    return datetime.strptime(time_string, format_str)
