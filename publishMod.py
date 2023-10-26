import paho.mqtt.client as mqtt
import random
import os
import sys
import platform
import time
import threading
import itertools

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

class Klien():
    def __init__(self):
        self.mqtt_server = "mqtt.eclipseprojects.io"
        self.mqtt_topic = ["klien_cekESP", "klien_updateTunggal"]
        self.payload = time.ctime()
        self.client = mqtt.Client(f"Klien-{random.randint(1, 999)}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_unsubscribe = self.on_unsubscribe

        self.done = False
        self.onESP = []

        self.pesan = ""
        self.updated = False

    def on_connect(self, client, userdata, flags, rc):
        print("\rTerhubung dengan server MQTT")
        self.menu()
        
    def on_message(self, client, userdata, msg):
        self.pesan = str(msg.payload.decode('utf-8'))
        if msg.topic == self.mqtt_topic[0]:
            print(".", end=" ")
            sys.stdout.flush()
            self.onESP.append(self.pesan)
        elif msg.topic == self.mqtt_topic[1]:
            self.result()

    def on_unsubscribe(self, client, userdata, mid):
        pass

    def set_loading(self, func=None, sec=None):
        self.done = False
        ti = threading.Timer(sec, func)
        ti.start()
        th = threading.Thread(target=self.animate)
        th.start()

    def animate(self):
        for c in itertools.cycle(["⢿ ", "⣻ ", "⣽ ", "⣾ ", "⣷ ", "⣯ ", "⣟ ", "⡿ "]):
            if self.done:
                break
            sys.stdout.write('\rloading ' + c)
            sys.stdout.flush()
            time.sleep(0.1)

    def updateTunggal(self):
        self.done = True
        clear()
        for i in range(len(self.onESP)):
            print(f"{i+1}. {self.onESP[i]}")
        print("0. Kembali\nMasukkan urutan ESP untuk di update")
        pilih = input("-> ")
        try:
            pilih = int(pilih)
        except:
            print("Masukan harus Angka")
            time.sleep(2)
            self.updateTunggal()
        else:
            if pilih == 0:
                self.menu()
            else:
                topic = self.onESP[pilih - 1]
                self.client.subscribe(self.mqtt_topic[1])
                self.client.publish(topic, self.payload)
                self.set_loading(self.result, 8)
                clear()

    def result(self):
        self.done = True
        if self.updated:
            print(f"Proses update firmware pada {self.pesan} berhasil")
        else:
            print("gagal")
        input("Tekan ENTER untuk melanjutkan")
        self.menu()

    def cekESP(self, route):
        self.done = True
        topic = "cekESP"
        self.onESP.clear()
        self.client.subscribe(self.mqtt_topic[0])
        self.client.publish(topic, self.payload)
        if route == 1:
            self.set_loading(self.updateTunggal, 3)
        elif route == 9:
            self.menu()
        elif route == 0:
            sys.exit()
        else:
            self.menu()

    def menu(self):
        clear()
        # self.done = True
        self.client.unsubscribe(self.mqtt_topic)
        print("1. Update per-satu ESP\n9. Kembali\n0. Keluar")
        pilih = int(input("-> "))
        self.cekESP(pilih)
        
    def run(self):
        print("\rMembangun koneksi dengan MQTT ...")
        self.client.connect(self.mqtt_server, 1883, 60)
        # self.set_loading(self.menu, 3)
        self.client.loop_forever()

if __name__ == "__main__":
    klien = Klien()
    klien.run()