import paho.mqtt.client as mqtt
import random
import time
import os
import platform
import json

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

class TempMqtt():
    def __init__(self) -> None:
        # Alamat broker MQTT
        self.uniq_ID = f"ESP-{random.randint(1, 999)}"
        # self.uniq_ID = f"ESP-{self.generate_random_mac()}"
        self.broker_address = "192.168.1.71"  # Ganti dengan alamat broker MQTT yang sesuai
        self.mqtt_topic_sub = "OTAUpdate/esp"
        self.mqtt_topic_pub = "OTAUpdate/klien"
        self.version = 1
        # Inisialisasi klien MQTT
        self.client = mqtt.Client(self.uniq_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def generate_random_mac(self):
        mac = [0x00, 0x16, 0x3e, random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
        mac_address = ':'.join(map(lambda x: "{:02x}".format(x), mac))
        return mac_address
    
    def updating(self):
        pesan = {
            'command': 'update',
            'espId': self.uniq_ID,
            'progress': 'success',
        }
        self.version += 1
        
        self.client.publish(self.mqtt_topic_pub, json.dumps(pesan))
        print(f'Publish message on topic {self.mqtt_topic_pub}: {pesan}\n')

    # Fungsi yang akan dipanggil saat koneksi ke broker MQTT berhasil
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.client.subscribe(self.mqtt_topic_sub)
        clear()

    # Fungsi yang akan dipanggil saat pesan diterima dari topik "update"
    def on_message(self, client, userdata, msg):
        strMsg = str(msg.payload.decode('utf-8'))
        print("Received message on topic '" + msg.topic + "': " + strMsg)
        if strMsg == 'check':
            pesan = {
                'command': "checked",
                'espId': self.uniq_ID,
                'version': self.version,
            }
            self.client.publish(self.mqtt_topic_pub, json.dumps(pesan))
            print(f'Publish message on topic {self.mqtt_topic_pub}: {pesan}\n')
        elif strMsg == self.uniq_ID:
            pesan = {
                'command': 'update',
                'espId': self.uniq_ID,
                'progress': 'updating',
            }
            self.client.publish(self.mqtt_topic_pub, json.dumps(pesan))
            print(f'Publish message on topic {self.mqtt_topic_pub}: {pesan}\n')
            self.updating()
        # if msg.topic == self.mqtt_topic[0]:
        #     self.client.publish("OTAUpdate/klien/cekESP", self.uniq_ID)
        # elif msg.topic == self.uniq_ID:
        #     time.sleep(5)
        #     self.client.publish("OTAUpdate/klien/updateTunggal", self.uniq_ID)
    
    def run(self):
        # Koneksi ke broker MQTT
        self.client.connect(self.broker_address, 1883, 60)
        self.client.loop_start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\rDisconnecting from broker...")
            self.client.disconnect()
            self.client.loop_stop()

if __name__ == "__main__":
    mqtt = TempMqtt()
    mqtt.run()