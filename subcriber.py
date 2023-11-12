import paho.mqtt.client as mqtt
import platform
import os

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

# Fungsi yang akan dipanggil saat koneksi ke broker MQTT berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("OTAUpdate/klien")
    # Berlangganan ke topik "update"

# Fungsi yang akan dipanggil saat pesan diterima dari topik "update"
def on_message(client, userdata, msg):
    print("Received message on topic '" + msg.topic + "': " + str(msg.payload))

# Inisialisasi klien MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Alamat broker MQTT
broker_address = "192.168.1.71"  # Ganti dengan alamat broker MQTT yang sesuai

# Koneksi ke broker MQTT
client.connect(broker_address, 1883, 60)

# Teruskan koneksi ke broker dan menunggu pesan
client.loop_start()
try:
    while True:
        input()
        clear()
except KeyboardInterrupt:
    print("\rDisconnecting from broker...")
    client.disconnect()
    client.loop_stop()
