import paho.mqtt.client as mqtt
import random
import time
import os
import platform

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

class TempMqtt():
    def __init__(self) -> None:
        # Alamat broker MQTT
        self.ID = f"ESP-{random.randint(1, 999)}"
        self.broker_address = "mqtt.eclipseprojects.io"  # Ganti dengan alamat broker MQTT yang sesuai
        # Inisialisasi klien MQTT
        self.client = mqtt.Client(self.ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    # Fungsi yang akan dipanggil saat koneksi ke broker MQTT berhasil
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.client.subscribe("cekESP")
        self.client.subscribe(self.ID)
        clear()

    # Fungsi yang akan dipanggil saat pesan diterima dari topik "update"
    def on_message(self, client, userdata, msg):
        pesan = str(msg.payload.decode('utf-8'))
        print("Received message on topic '" + msg.topic + "': " + pesan)
        if msg.topic == "cekESP":
            self.client.publish("klien_cekESP", self.ID)
        elif msg.topic == self.ID:
            time.sleep(5)
            self.client.publish("klien_updateTunggal", self.ID)

    def run(self):
        # Koneksi ke broker MQTT
        self.client.connect(self.broker_address, 1883, 60)
        self.client.loop_forever()

if __name__ == "__main__":
    mqtt = TempMqtt()
    mqtt.run()