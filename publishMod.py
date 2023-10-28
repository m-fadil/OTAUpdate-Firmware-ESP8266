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

class Mqtt():
    def __init__(self) -> None:
        self.mqtt_server = "mqtt.eclipseprojects.io"
        self.mqtt_topic = ["klien_cekESP", "klien_updateTunggal"]
        self.payload = time.ctime()
        self.client = mqtt.Client(f"Klien-{random.randint(1, 999)}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_unsubscribe = self.on_unsubscribe

        self.done = self.updated = self.connected = False
        self.hasil = {"updated": False, "text": ""}
        self.onESP = []
    
    def on_connect(self, client, userdata, flags, rc):
        self.done = self.connected = True
        print("\rTerhubung dengan server MQTT")
        
    def on_message(self, client, userdata, msg):
        pesan = str(msg.payload.decode('utf-8'))
        if msg.topic == self.mqtt_topic[0]:
            self.onESP.append(pesan)
        elif msg.topic == self.mqtt_topic[1]:
            self.done = self.hasil["updated"] = True
            self.hasil["text"] = pesan

    def on_unsubscribe(self, client, userdata, mid):
        pass

    def set_timeout(self, func, sec):
        ti = threading.Timer(sec, func)
        ti.start()

    def set_loading(self, sec=None, method="join", next=None):
        def animate(func=next):
            timeout = time.time() + sec if sec != None else True
            for c in itertools.cycle(["⢿ ", "⣻ ", "⣽ ", "⣾ ", "⣷ ", "⣯ ", "⣟ ", "⡿ "]):
                if self.done or (not(time.time() < timeout) and sec != None):
                    if func == None:
                        break
                    else:
                        return func()
                sys.stdout.write('\rloading ' + c)
                sys.stdout.flush()
                time.sleep(0.1)
        self.done = False
        th = threading.Thread(target=animate)
        th.start()
        if method == "join": th.join()
        
    def connect(self, func):
        self.set_loading(10, "thread", func)
        print("\rMembangun koneksi dengan MQTT ...")
        self.client.connect(self.mqtt_server, 1883, 60)
        self.client.loop_start()

class Klien(Mqtt):
    def __init__(self) -> None:
        super().__init__()

    def result(self):
        clear()
        if self.hasil["updated"]:
            print(f"\rProses update firmware pada {self.hasil['text']} berhasil")
        else:
            print("gagal update")
        _ = input("\nTekan ENTER untuk melanjutkan")
        self.menu()

    def updateTunggal(self):
        clear()
        for i in range(len(self.onESP)):
            print(f"{i+1}. {self.onESP[i]}")
        print("0. Kembali\nMasukkan urutan ESP untuk di update")
        pilih = input("-> ")
        try:
            pilih = int(pilih)
        except:
            print("Masukan harus angka")
            time.sleep(2)
            self.updateTunggal()
        else:
            if pilih == 0:
                self.menu()
            else:
                topic = self.onESP[pilih - 1]
                self.client.subscribe(self.mqtt_topic[1])
                self.client.publish(topic, self.payload)
                self.set_loading(7, next=self.result)

    def cekESP(self):
        topic = "cekESP"
        self.onESP.clear()
        self.client.subscribe(self.mqtt_topic[0])
        self.client.publish(topic, self.payload)

    def menu(self):
        clear()
        if not self.connected:
            print("Gagal terkoneksi dengan server Mqtt")
            time.sleep(2)
            return self.run()
        self.client.unsubscribe(self.mqtt_topic)
        print("1. Update per-satu ESP\n0. Keluar")
        pilih = input("-> ")
        try:
            pilih = int(pilih)
        except:
            print("Masukan harus angka")
            time.sleep(2)
            self.menu()
        else:
            if pilih == 1:
                self.cekESP()
                # self.set_timeout(self.updateTunggal, 3)
                self.set_loading(3, next=self.updateTunggal)
            elif pilih == 0:
                sys.exit()
            else:
                self.menu()

    def run(self):
        self.connect(self.menu)
            
if __name__ == "__main__":
    klien = Klien()
    klien.run()