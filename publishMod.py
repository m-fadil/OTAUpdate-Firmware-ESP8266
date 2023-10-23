import paho.mqtt.client as mqtt
import random
import os
import platform
import time

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def connectMqtt():
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        _ = input('->')
        print(_)
        
    def on_message(client, userdata, msg):
        pesan = str(msg.payload.decode('utf-8'))
        print("Received message on topic '" + msg.topic + "': " + pesan)

    def on_unsubscribe(client, userdata, mid):
        print("Unsubscribed from topic")

    mqtt_server = "mqtt.eclipseprojects.io"
    mqtt_payload = ""
    mqtt_topic = ""
    client = mqtt.Client(f"Klien-{random.randint(1, 999)}")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_unsubscribe = on_unsubscribe
    client.connect(mqtt_server, 1883, 60)
    client.loop_start()

if __name__ == "__main__":
    connectMqtt()