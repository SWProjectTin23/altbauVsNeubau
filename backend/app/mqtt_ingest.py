from flask import Flask
import paho.mqtt.client as mqtt

app = Flask(__name__)

MQTT_BROKER = 'localhost'  
MQTT_PORT = 1883
MQTT_TOPIC = 'dhbw/ai/si2023/01/ikea/01'

def on_connect(client, userdata, flags, rc):
    print(f"Verbunden mit Code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Nachricht empfangen: Topic: {msg.topic}, Payload: {msg.payload.decode()}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()  # Hintergrund-Thread starten

@app.route('/')
def index():
    return "MQTT-Client läuft!"

if __name__ == '__main__':
    app.run(debug=True)
