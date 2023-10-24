import paho.mqtt.client as mqtt
import time

mqtt_server = "mqtt.eclipseprojects.io"  # Ganti dengan alamat broker MQTT yang Anda gunakan
mqtt_topic = "cekESP"
mqtt_payload = "Pesan dari Python"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    
client = mqtt.Client()
client.on_connect = on_connect

client.connect(mqtt_server, 1883, 60)

while True:
    client.publish(mqtt_topic, mqtt_payload)
    print("Pesan terkirim: " + mqtt_payload)
    time.sleep(2)  # Kirim pesan setiap 2 detik
