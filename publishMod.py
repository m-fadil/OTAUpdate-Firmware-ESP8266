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

done = False
onESP = []

pesan = ""
updated = False

def on_connect(client, userdata, flags, rc):
    print("\rTerhubung dengan server MQTT")
    
def on_message(client, userdata, msg):
    global done
    pesan = str(msg.payload.decode('utf-8'))
    if msg.topic == mqtt_topic[0]:
        print(".", end=" ")
        sys.stdout.flush()
        onESP.append(pesan)
    elif msg.topic == mqtt_topic[1]:
        done = True
        result()

def on_unsubscribe(client, userdata, mid):
    pass

def set_timeout(func, sec):
    ti = threading.Timer(sec, func)
    ti.start()

def set_wait(sec):
    timeout = time.time() + 3
    def loop():
        while time.time() < timeout:
            time.sleep(0.1)
    th = threading.Thread(target=loop)
    th.start()

def set_loading():
    global done
    def animate():
        global done
        for c in itertools.cycle(["⢿ ", "⣻ ", "⣽ ", "⣾ ", "⣷ ", "⣯ ", "⣟ ", "⡿ "]):
            if done:
                break
            sys.stdout.write('\rloading ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
    done = False
    th = threading.Thread(target=animate)
    th.start()

def updateTunggal():
    done = True
    clear()
    for i in range(len(onESP)):
        print(f"{i+1}. {onESP[i]}")
    print("0. Kembali\nMasukkan urutan ESP untuk di update")
    pilih = input("-> ")
    try:
        pilih = int(pilih)
    except:
        print("Masukan harus Angka")
        time.sleep(2)
        updateTunggal()
    else:
        if pilih == 0:
            menu()
        else:
            topic = onESP[pilih - 1]
            client.subscribe(mqtt_topic[1])
            client.publish(topic, payload)
            set_loading()
            clear()

def result():
    if updated:
        print(f"Proses update firmware pada {pesan} berhasil")
    else:
        print("gagal")
    input("Tekan ENTER untuk melanjutkan")
    menu()

def cekESP(route):
    topic = "cekESP"
    onESP.clear()
    client.subscribe(mqtt_topic[0])
    client.publish(topic, payload)

def menu():
    clear()
    # done = True
    client.unsubscribe(mqtt_topic)
    print("1. Update per-satu ESP\n9. Kembali\n0. Keluar")
    pilih = int(input("-> "))
    if pilih == 1:
        cekESP(pilih)
        set_timeout(updateTunggal, 3)
        return
    elif pilih == 9:
        menu()
    elif pilih == 0:
        sys.exit()
    else:
        menu()
    
def run():
    print("\rMembangun koneksi dengan MQTT ...")
    client.connect(mqtt_server, 1883, 60)
    set_timeout(menu, 3)
    # set_wait(3)
    client.loop_start()

if __name__ == "__main__":
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_unsubscribe = on_unsubscribe
    run()