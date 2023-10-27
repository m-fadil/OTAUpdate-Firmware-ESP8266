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

mqtt_server = "mqtt.eclipseprojects.io"
mqtt_topic = ["klien_cekESP", "klien_updateTunggal"]
payload = time.ctime()
client = mqtt.Client(f"Klien-{random.randint(1, 999)}")

done = updated = False
text = ""
onESP = []


def on_connect(client, userdata, flags, rc):
    global done
    print("\rTerhubung dengan server MQTT")
    time.sleep(1)
    done = True
    
def on_message(client, userdata, msg):
    global done, updated, text
    pesan = str(msg.payload.decode('utf-8'))
    if msg.topic == mqtt_topic[0]:
        print(".", end=" ")
        sys.stdout.flush()
        onESP.append(pesan)
    elif msg.topic == mqtt_topic[1]:
        done = updated = True
        text = pesan

def on_unsubscribe(client, userdata, mid):
    pass

def set_timeout(func, sec):
    ti = threading.Timer(sec, func)
    ti.start()

def set_loading(method="default", sec=None):
    global done
    def animate():
        global done
        timeout = time.time() + sec if sec != None else True
        for c in itertools.cycle(["⢿ ", "⣻ ", "⣽ ", "⣾ ", "⣷ ", "⣯ ", "⣟ ", "⡿ "]):
            if done or (not(time.time() < timeout) and sec != None):
                break
            sys.stdout.write('\rloading ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
    done = False
    th = threading.Thread(target=animate)
    th.start()
    if method == "join": th.join()

def result():
    clear()
    global updated, text
    if updated:
        print(f"\rProses update firmware pada {text} berhasil")
    else:
        print("gagal update")
    _ = input("\nTekan ENTER untuk melanjutkan")
    menu()

def updateTunggal():
    clear()
    for i in range(len(onESP)):
        print(f"{i+1}. {onESP[i]}")
    print("0. Kembali\nMasukkan urutan ESP untuk di update")
    pilih = input("-> ")
    try:
        pilih = int(pilih)
    except:
        print("Masukan harus angka")
        time.sleep(2)
        updateTunggal()
    else:
        if pilih == 0:
            menu()
        else:
            topic = onESP[pilih - 1]
            client.subscribe(mqtt_topic[1])
            client.publish(topic, payload)
            set_loading("join", 7)
            result()

def cekESP():
    topic = "cekESP"
    onESP.clear()
    client.subscribe(mqtt_topic[0])
    client.publish(topic, payload)

def menu():
    global done
    done = True
    clear()
    client.unsubscribe(mqtt_topic)
    print("1. Update per-satu ESP\n0. Keluar")
    pilih = input("-> ")
    try:
        pilih = int(pilih)
    except:
        print("Masukan harus angka")
        time.sleep(2)
        menu()
    else:
        if pilih == 1:
            cekESP()
            set_timeout(updateTunggal, 3)
        elif pilih == 0:
            sys.exit()
        else:
            menu()
    
def run():
    print("\rMembangun koneksi dengan MQTT ...")
    client.connect(mqtt_server, 1883, 60)
    set_loading(sec=3)
    menu()
    client.loop_start()

if __name__ == "__main__":
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_unsubscribe = on_unsubscribe
    run()