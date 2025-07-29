import json
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "aicon.dhbw-heidenheim.de"
MQTT_PORT = 1883
MQTT_TOPIC = "dhbw/ai/si2023/01/ikea/01"
MQTT_USER = "haenisch"
MQTT_PASS = "geheim"
DATA_FILE = "data.json"
SEND_INTERVAL = 20  # Sekunden

def main():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Verbindung zum MQTT Broker fehlgeschlagen: {e}")
        return

    client.loop_start()

    try:
        while True:
            try:
                with open(DATA_FILE, "r") as f:
                    payload = json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der JSON-Datei: {e}")
                time.sleep(SEND_INTERVAL)
                continue

            try:
                msg_info = client.publish(MQTT_TOPIC, json.dumps(payload))
                if msg_info.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"JSON erfolgreich an {MQTT_TOPIC} gesendet.")
                else:
                    print(f"Fehler beim Senden: Rückgabecode {msg_info.rc}")
            except Exception as e:
                print(f"Fehler beim Senden der MQTT-Nachricht: {e}")

            time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        print("Abbruch durch Nutzer")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
