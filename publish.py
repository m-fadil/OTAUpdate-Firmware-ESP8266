import paho.mqtt.client as mqtt
import time

mqtt_server = "192.168.1.71"  # Ganti dengan alamat broker MQTT yang Anda gunakan
mqtt_topic_sub = "OTAUpdate/esp"
mqtt_payload = "ESP-Sensor_Suhu"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect

client.connect(mqtt_server, 1883, 60)

client.loop_start()
try:
    while True:
        if client.is_connected():
            payload = input()
            client.publish(mqtt_topic_sub, payload)
            print("Pesan terkirim: " + payload)
except KeyboardInterrupt:
    print("\rDisconnecting from broker...")
    client.disconnect()
    client.loop_stop()