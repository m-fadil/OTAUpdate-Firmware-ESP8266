from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import paho.mqtt.client as mqtt
import keyboard
import requests
import random
import time
import json
import os

def clear(withText=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    if withText != None: print(withText)

class Klien():
    def __init__(self) -> None:
        self.mqtt_server = "20.2.86.174"
        self.mqtt_port = 1883
        self.mqtt_topic_sub = "OTAUpdate/klien"
        self.mqtt_topic_pub = "OTAUpdate/esp"

        self.client = mqtt.Client(f"Klien-{random.randint(1, 999)}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.espList = []

    def on_connect(self, client, userdata, flags, rc):
        print("Terhubung dengan server MQTT")
        self.client.subscribe(self.mqtt_topic_sub)
        
    def on_message(self, client, userdata, message):
        pesan = str(message.payload.decode("utf-8"))
        self.handle_message(pesan)

    def cek_esp(self, route):
        self.espList.clear()
        self.client.publish(self.mqtt_topic_pub, "check")
        time.sleep(1.5)
        route()

    def uplaod_firmware(self, index):
        clear()
        print("[b] Kembali")
        completer = PathCompleter()
        file_path = prompt("\nMasukkan file path firmware: ", completer=completer)
        if file_path.lower() in ["b", ""]:
            pass
        else:
            try:
                clear()
                print("Loading...", end="\r", flush=True)
                respons = requests.post('http://20.205.21.101:3000/upload', files={'file': open(file_path, 'rb')})
            except:
                input("Terjadi kesalahan pada server\n\nTekan ENTER untuk melanjutkan")            
            else:
                if respons.status_code == 200:
                    if index == "all":
                        topic = f"{self.mqtt_topic_pub}/all"
                        self.client.publish(topic, "start")
                    else:
                        for idx in index:
                            topic = f"{self.mqtt_topic_pub}/{self.espList[idx - 1]["mac"]}"
                            self.client.publish(topic, "start")
                    self.update_status()
                elif respons.status_code == 400:
                    input(f"Error: {respons.text}\n\nTekan ENTER untuk melanjutkan") # Diubah dengan status kode dan pesan dari server  
                else:
                    input("Erorr tidak diketahui\n\nTekan ENTER untuk melanjutkan") # Diubah dengan status kode dan pesan dari server  


    def update_status(self):
        tick = time.time()
        while True:
            if time.time() >= tick:
                clear()
                for i, esp in enumerate(self.espList):
                    if "progress" in esp:
                        print(f"{i + 1}. {esp["espId"]} [{esp["progress"]}] {esp["update_time"] if "update_time" in esp else ""}")
                print("\nTekan ESCAPE untuk kembali")
                tick += 0.25
            if keyboard.is_pressed("escape"): break

    def menu(self):
        clear()
        for index, esp in enumerate(self.espList):
            print(f"{index + 1}. {esp["espId"]:<16} version: {esp["version"]:<4} ({esp["mac"]})")
        inp = input("\n[a] Update semua\n[c] Cek status update\n[r] Muat ulang\n[q] Keluar\n\nMasukkan urutan ESP untuk di update\n-> ")
        if inp.lower() == "a":
            index = [i+1 for i in range(len(self.espList))]
            self.uplaod_firmware(index)
        elif inp.lower() == "c":
            self.update_status()
        elif inp.lower() == "r":
            clear("Memuat ulang ..")
            self.cek_esp(self.menu)
        elif inp.lower() == "q":
            exit(0)
        else:
            try:
                index = [int(element) for element in "".join(inp.split(" ")).split(",")]
            except ValueError as e:
                print(f"Error: {e}. Pastikan semua elemen adalah integer.")
            else:
                self.uplaod_firmware(index)
        self.menu()
        
    def handle_message(self, message):
        pesan = json.loads(message)
        if pesan["command"] == "checked":
            self.espList.append({
                "espId": pesan["espId"],
                "version": pesan["version"],
                "mac": pesan["mac"],
            })
        elif pesan["command"] == "update":
            for esp in self.espList:
                if esp["espId"] == pesan["espId"] and esp["mac"] == pesan["mac"]:
                    esp["version"] = pesan["version"]
                    esp["progress"] = pesan["progress"]
                    if "update_time" in pesan:
                        esp["update_time"] = pesan["update_time"]

    def start(self):
        print("Membangun koneksi dengan MQTT ...")
        self.client.connect(self.mqtt_server, self.mqtt_port, 60)
        self.client.loop_start()
        try:
            while not self.client.is_connected():
                pass
            self.cek_esp(self.menu)
        except KeyboardInterrupt:
            exit(0)
        

if __name__ == "__main__":
    klien = Klien()
    klien.start()