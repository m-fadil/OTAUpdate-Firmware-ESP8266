from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import paho.mqtt.client as mqtt
import keyboard
import requests
import solara
import random
import time
import json
import os

class Klien():
    def __init__(self) -> None:
        self.mqtt_server = "172.29.192.1"
        self.mqtt_port = 1883
        self.mqtt_topic_sub = "OTAUpdate/klien"
        self.mqtt_topic_pub = "OTAUpdate/esp"

        self.client = mqtt.Client(f"Klien")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.esp_list = []

    def on_connect(self, client, userdata, flags, rc):
        print("Terhubung dengan server MQTT")
        self.client.subscribe(self.mqtt_topic_sub)
        
    def on_message(self, client, userdata, message):
        msg = str(message.payload.decode("utf-8"))

        pesan = json.loads(msg)
        if pesan['command'] == 'checked':
            self.esp_list.append({
                'espId': pesan['espId'],
                'mac': pesan['mac'],
                'version': pesan['version'],
            })
        elif pesan['command'] == 'update':
            for esp in self.esp_list:
                if esp['espId'] == pesan['espId']:
                    esp['version'] = pesan['version']
                    esp['progress'] = pesan['progress']

    def on_disconnect(self, client, userdata, rc):
        print("disconnect dengan server MQTT")
        self.client.loop_stop()

    def start(self):
        print("Membangun koneksi dengan MQTT ...")
        self.client.connect(self.mqtt_server, self.mqtt_port, 60)
        self.client.loop_start()
        
app = Klien()
app.start()

updating = solara.reactive(False)
esp_list = solara.reactive([])
checked_esp = solara.reactive([])

@solara.component
def page():
    solara.AppBarTitle("OTA Update Firmware ESP8266")
    
    if updating.value:
        updating_esp()
    else:
        listing_esp()
    

@solara.component
def listing_esp():
    click, use_click = solara.use_state(1)

    def cek_esp():
        app.esp_list.clear()
        app.client.publish(app.mqtt_topic_pub, "check")
        time.sleep(2)
        esp_list.set(app.esp_list)
        return esp_list.value

    def update_esp(command="single"):
        if command == "all":
            checked_esp.set([esp["espId"] for esp in esp_list.value])
        updating.set(True)

    result = solara.use_thread(cek_esp, dependencies=[click])

    if result.state == solara.ResultState.FINISHED:
        with solara.Row():
            solara.Button("Refresh", on_click=lambda: use_click(not click))
        with solara.Card("List ESP"):
            solara.SelectMultiple("Pilih ESP",checked_esp , [esp["espId"] for esp in result.value])
            solara.Markdown(f"**Selected**: {', '.join(str(x) for x in checked_esp.value)}")
        with solara.Row(gap="12px", justify="end"):
            if len(checked_esp.value) != 0:
                solara.Button("Update", on_click=update_esp, color="primary")
            solara.Button("Update All", on_click=lambda: update_esp("all"), color="warning")


    elif result.state == solara.ResultState.ERROR:
        solara.Error(f"Error occurred: {result.error}")

    else:
        solara.Info(f"Running... (status = {result.state})")
        solara.ProgressLinear(True)

@solara.component
def updating_esp():
    for esp_id in checked_esp.value:
        app.client.publish(f"{app.mqtt_topic_pub}/{next(esp["mac"] for esp in esp_list.value if esp["espId"] == esp_id)}", "start")
        with solara.Card(f"Updating {esp_id}..."):
            
            solara.Text(str([listed["espId"] for listed in esp_list.value if listed["espId"] == esp_id]))
            solara.ProgressLinear(True)

    solara.Button("Main menu", on_click=lambda: updating.set(not updating.value))