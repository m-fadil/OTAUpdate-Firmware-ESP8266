import paho.mqtt.client as mqtt
import random
import os
import platform
import time
import json

mqtt_server = '192.168.1.71'
mqtt_topic_sub = 'OTAUpdate/klien'
mqtt_topic_pub = 'OTAUpdate/esp'
client = mqtt.Client(f'Klien-{random.randint(1, 999)}')
espList = []

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def cekESP():
    espList.clear()
    client.subscribe(mqtt_topic_sub)
    client.publish(mqtt_topic_pub, 'check')


def updateStatus():
    clear()
    time.sleep(1)
    for i, esp in enumerate(espList):
        if 'progress' in esp:
            print(f'{i + 1}. {esp["espId"]} [{esp["progress"]}]')
    _ = input('\nTekan ENTER untuk kembali')

def menu():
    time.sleep(1.5)
    clear()
    for index, esp in enumerate(espList):
        print(f'{index + 1}. {esp['espId']} version: {esp['version']}')
    inp = input('\n[c] Cek status update\n[r] Muat ulang\n[ctrl+c] Keluar\nMasukkan urutan ESP untuk di update\n-> ')
    if inp.lower() == 'r':
        print('Memuat ulang ..')
        cekESP()
    elif inp.lower() == 'c':
        updateStatus()
    elif inp.lower() == 'dev':
        print(espList)
        _ = input()
    else:
        if len(inp) > 1:
            try:
                index = [int(element) for element in ''.join(inp.split(' ')).split(',')]
            except ValueError as e:
                print(f"Error: {e}. Pastikan semua elemen dalam array adalah integer.")
            else:
                for idx in index:
                    client.publish(mqtt_topic_pub, espList[idx - 1]['espId'])
                updateStatus()
        else:
            try:
                index = int(inp) - 1
            except:
                _ = input('terjadi error')
            else:
                client.publish(mqtt_topic_pub, espList[index]['espId'])
                updateStatus()

def handle_message(message):
    pesan = json.loads(message)
    if pesan['command'] == 'checked':
        espList.append({
            'espId': pesan['espId'],
            'version': pesan['version'],
        })
    elif pesan['command'] == 'update':
        for esp in espList:
            if esp['espId'] == pesan['espId']:
                esp['version'] = pesan['version']
                esp['progress'] = pesan['progress']

def on_connect(client, userdata, flags, rc):
    print('Terhubung dengan server MQTT')
    cekESP()

def on_message(client, userdata, msg):
    pesan = str(msg.payload.decode('utf-8'))
    handle_message(pesan)

if __name__ == '__main__':
    client.on_connect = on_connect
    client.on_message = on_message
    print('Membangun koneksi dengan MQTT ...')
    client.connect(mqtt_server, 1883, 60)
    client.loop_start()
    try:
        while True:
            if client.is_connected():
                menu()
    except KeyboardInterrupt:
        print("\rDisconnecting from broker...")
        client.disconnect()
        client.loop_stop()