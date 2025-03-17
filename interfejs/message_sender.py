import paho.mqtt.client as mqtt
import json

class MQTT_data_provider:
    def __init__(self, broker, port, username=None, password=None, main_window=None):
        self.broker = broker
        self.port = int(port)
        self.username = username
        self.password = password
        self.main_window = main_window

        self.active_request_topic = "active/request"
        self.active_response_topic = "active/response"

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.connect()

    def on_connect(self, client, userdata, flags, rc, data):
        client.subscribe(self.active_response_topic, qos=1)

    def on_message(self, client, userdata, msg):
        print(f"Otzymano wiadomość: {msg.payload.decode()} oznaczoną tematem: {msg.topic}")
        if(msg.topic==self.active_response_topic):
            self.main_window.add_new_sensor_to_combobox2(msg.payload.decode());

    def connect(self):
        print("pol")
        print(self.client.connect(self.broker, self.port, 60))

        self.client.loop_start() 
    
    def send_read_type_data(self, read_type, sensor_id, freq, threshold, series_time):
        topic = "type/all" if(sensor_id=="Wszystkie") else ("type/"+sensor_id)
        message_dict = {
            "type": read_type,
            "freq": freq,
            "threshold": threshold,
            "time" : series_time
        }
        message_str = json.dumps(message_dict,separators=(',',':'))
        self.client.publish(topic, message_str)
    
    def request_active(self):
        print("Wysłano active/request")
        self.client.publish(self.active_request_topic,"",qos=2)
