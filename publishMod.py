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

class Mqtt():
    def __init__(self):
        self.mqtt_server = "mqtt.eclipseprojects.io"
        self.mqtt_payload = ""
        self.mqtt_topic = ""
        self.client = mqtt.Client(f"Klien-{random.randint(1, 999)}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_unsubscribe = self.on_unsubscribe
        
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        
    def on_message(self, client, userdata, msg):
        pesan = str(msg.payload.decode('utf-8'))
        print("Received message on topic '" + msg.topic + "': " + pesan)

    def on_unsubscribe(self, client, userdata, mid):
        print("Unsubscribed from topic")

    def run(self):
        self.client.connect(self.mqtt_server, 1883, 60)
        self.client.loop_start()

if __name__ == "__main__":
    klien = Mqtt()
    klien.run()