import paho.mqtt.client as mqtt
import random
import os
import sys
import platform
import time
import threading

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

class Klien():
    def __init__(self):
        self.mqtt_server = "mqtt.eclipseprojects.io"
        self.client = mqtt.Client(f"Klien-{random.randint(1, 999)}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_unsubscribe = self.on_unsubscribe
        self.onESP = []

    def on_connect(self, client, userdata, flags, rc):
        print("Terhubung dengan server MQTT")
        
    def on_message(self, client, userdata, msg):
        pesan = str(msg.payload.decode('utf-8'))
        if msg.topic == "klien_cekESP":
            print(".", end=" ")
            sys.stdout.flush()
            self.onESP.append(pesan)

    def on_unsubscribe(self, client, userdata, mid):
        print("Unsubscribed from topic")

    def set_timeout(sefl, func, sec):
        t = threading.Timer(sec, func)
        t.start()

    def cekESP(self):
        topic = "cekESP"
        payload = "cek"
        self.onESP.clear()
        self.client.subscribe("klien_cekESP")
        self.client.publish(topic, payload)
        clear()
        print("memuat ESP")
        self.set_timeout(self.menu, 3)

    def menu(self):
        clear()
        print(f"\n{self.onESP}")
        print("1. Cek ESP yang aktif dan terhubung dengan MQTT\n0. Keluar")
        pilih = int(input())
        if pilih == 1:
            self.cekESP()
        elif pilih == 0:
            sys.exit()
        
    def run(self):
        self.client.connect(self.mqtt_server, 1883, 60)
        print("Membangun koneksi dengan MQTT ...")
        self.client.loop_start()
        self.set_timeout(self.menu, 3)

if __name__ == "__main__":
    klien = Klien()
    klien.run()