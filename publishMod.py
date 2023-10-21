import paho.mqtt.client as mqtt
import time
import sys

mqtt_server = "mqtt.eclipseprojects.io"  # Ganti dengan alamat broker MQTT yang Anda gunakan
mqtt_topic = "update1111"
mqtt_payload = "Pesan dari Python"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    
client = mqtt.Client()
client.on_connect = on_connect

client.connect(mqtt_server, 1883, 60)

while True:
    print('\n\n1.\tUpdate salah satu\n2.\tUpdate semua')
    pilihan = int(input('-> '));
    if pilihan == 1:
        print('\nEsp dengan nomor urut berapa 1 - 99?')
        urutan = int(input('-> '))
        mqtt_payload = f"ESP-{urutan}"
    else:
        mqtt_payload = "ESP-ALL"
    client.publish(mqtt_topic, mqtt_payload)
    print("Pesan terkirim: " + mqtt_payload)
    for i in range(8):
        print('.', end='')
        sys.stdout.flush()
        time.sleep(0.25)
    print()