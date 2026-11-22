import paho.mqtt.client as mqtt
import json, time, random
from datetime import datetime

BROKER = "localhost"
PORT = 1883
TOPIC_SENSOR = "iot/sensor"
TOPIC_KONTROL = "iot/kontrol"
TOPIC_ALERT = "iot/alert"

lampu = "off"  # status lampu perangkat (diubah oleh perintah dari dashboard)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Terhubung ke broker (kode: {reason_code})")
    client.subscribe([(TOPIC_KONTROL, 0), (TOPIC_ALERT, 0)])


def on_message(client, userdata, msg):
    global lampu
    try:
        data = json.loads(msg.payload.decode())
    except ValueError:
        print(f"Pesan tidak valid di {msg.topic}: {msg.payload}")
        return

    if msg.topic == TOPIC_KONTROL:
        if data.get("device") == "lamp":
            lampu = "on" if data.get("action") == "on" else "off"
            print(f"<< Perintah diterima: LAMPU {lampu.upper()}")
    elif msg.topic == TOPIC_ALERT:
        print(f"<< ALERT dari server: {data.get('pesan')}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ESP32-Simulator")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

print("ESP32 Simulator berjalan... Ctrl+C untuk stop")
try:
    while True:
        data = {
            "suhu": round(random.uniform(25, 32), 1),
            "kelembaban": round(random.uniform(55, 80), 1),
            "lampu": lampu,
            "timestamp": datetime.now().isoformat(),
        }
        client.publish(TOPIC_SENSOR, json.dumps(data))
        print(f"-> Publish: {data}")
        time.sleep(3)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
