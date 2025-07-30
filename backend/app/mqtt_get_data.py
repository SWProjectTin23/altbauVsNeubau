from flask import Flask
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

MQTT_BROKER = 'aicon.dhbw-heidenheim.de'
MQTT_PORT = 1883
MQTT_TOPIC = 'dhbw/ai/si2023/01/+/+'

def on_connect(client, userdata, flags, rc):
    print(f"Verbunden mit Code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    Payload = msg.payload.decode()
    try:
        payload_dict = json.loads(Payload)
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Fehler beim Verarbeiten der Nachricht: {e}")

    value = payload_dict["value"]
    timestamp = payload_dict["timestamp"]

    print(f"Nachricht empfangen: Topic: {msg.topic}, value: {value}, timestamp: {timestamp}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

if __name__ == '__main__':
    mqtt_client.loop_start()
    app.run(debug=False)

