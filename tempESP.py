import paho.mqtt.client as mqtt
import random
import time

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
        # Berlangganan ke topik "update"
        self.client.subscribe("cekESP")

    # Fungsi yang akan dipanggil saat pesan diterima dari topik "update"
    def on_message(self, client, userdata, msg):
        pesan = str(msg.payload.decode('utf-8'))
        print("Received message on topic '" + msg.topic + "': " + pesan)
        if msg.topic == "cekESP":
            self.client.publish("klien_cekESP", self.ID)

    def run(self):
        # Koneksi ke broker MQTT
        self.client.connect(self.broker_address, 1883, 60)

        # Teruskan koneksi ke broker dan menunggu pesan
        """ timeout = time.time() + 5
        while time.time() < timeout:
            client.loop() """

        self.client.loop_forever()

if __name__ == "__main__":
    mqtt = TempMqtt()
    mqtt.run()