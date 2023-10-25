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
        self.mqtt_topic = ["klien_cekESP", "klien_updateTunggal"]
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
        pass

    def set_timeout(sefl, func, sec):
        t = threading.Timer(sec, func)
        t.start()

    def updateTunggal(self):
        clear()
        for i in range(len(self.onESP)):
            print(f"{i+1}. {self.onESP[i]}")
        print("0. Kembali\nMasukkan urutan ESP untuk di update")
        pilih = input("-> ")
        try:
            pilih = int(pilih)
        except:
            print("Masukan harus Angka atau q untuk keluar")
            time.sleep(2)
            self.updateTunggal()
        else:
            if pilih == 0:
                self.menu()
            else:
                topic = self.onESP[pilih - 1]
                payload = "update"
                self.client.subscribe(self.mqtt_topic[1])
                self.client.publish(topic, payload)
                clear()
                print("memuat ESP")
                self.set_timeout(self.menu, 3)

    def cekESP(self, route):
        topic = "cekESP"
        payload = "cek"
        self.onESP.clear()
        self.client.subscribe(self.mqtt_topic[0])
        self.client.publish(topic, payload)
        if route == 1:
            self.set_timeout(self.updateTunggal, 3)
        elif route == 9:
            self.menu()
        elif route == 0:
            sys.exit()
        else:
            self.menu()
        clear()
        print("memuat ESP")

    def menu(self):
        clear()
        self.client.unsubscribe(self.mqtt_topic)
        print("1. Update per-satu ESP\n9. Kembali\n0. Keluar")
        pilih = int(input("-> "))
        self.cekESP(pilih)
        
    def run(self):
        self.client.connect(self.mqtt_server, 1883, 60)
        print("Membangun koneksi dengan MQTT ...")
        self.client.loop_start()
        self.set_timeout(self.menu, 3)

if __name__ == "__main__":
    klien = Klien()
    klien.run()