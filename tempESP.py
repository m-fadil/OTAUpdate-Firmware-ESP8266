import paho.mqtt.client as mqtt
import time

# Fungsi yang akan dipanggil saat koneksi ke broker MQTT berhasil
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Berlangganan ke topik "update"
    client.subscribe("cekESP")

# Fungsi yang akan dipanggil saat pesan diterima dari topik "update"
def on_message(client, userdata, msg):
    pesan = str(msg.payload.decode('utf-8'))
    print("Received message on topic '" + msg.topic + "': " + pesan)
    if msg.topic == "cekESP":
        client.publish("update1111", "benar")

# Inisialisasi klien MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Alamat broker MQTT
broker_address = "mqtt.eclipseprojects.io"  # Ganti dengan alamat broker MQTT yang sesuai

# Koneksi ke broker MQTT
client.connect(broker_address, 1883, 60)

# Teruskan koneksi ke broker dan menunggu pesan
timeout = time.time() + 5
while time.time() < timeout:
    client.loop()
