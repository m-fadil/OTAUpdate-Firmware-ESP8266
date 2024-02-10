#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>
#include <ArduinoJson.h>

#define ssid "DESKTOP"
#define password "TmzXgd4Z"
#define mqtt_server "172.188.112.220"
#define mqtt_port 1883
#define mqtt_topic_sub "OTAUpdate/esp"
#define mqtt_topic_sub_all "OTAUpdate/esp/all"
#define mqtt_topic_pub "OTAUpdate/klien"
#define espId "ESP-Sensor_Suhu"
#define FIRMWARE_VERSION "0.3"
#define LED_1 2
#define LED_2 16
char macAddress[18];
char mqtt_self_topic_sub[35];

unsigned long start_time;
unsigned long end_time;
unsigned long update_time;

DynamicJsonDocument doc(1024);
String JSONPayload;

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  WiFi.mode(WIFI_STA);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  uint8_t mac[6];
  WiFi.macAddress(mac);
  sprintf(macAddress, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  sprintf(mqtt_self_topic_sub, "%s/%s", mqtt_topic_sub, macAddress);
}

void publish() {
  doc["espId"] = espId;
  doc["mac"] = macAddress;
  doc["version"] = FIRMWARE_VERSION;
  JSONPayload = "";
  serializeJson(doc, JSONPayload);
  client.publish(mqtt_topic_pub, JSONPayload.c_str());
  doc.clear();
}

void update_firmware() {
  Serial.println(F("Update start now!"));
  doc["command"] = "update";
  doc["progress"] = "updating";
  publish();

  t_httpUpdate_return ret = ESPhttpUpdate.update(espClient, "172.188.112.220", 8080, "/firmware/firmware_update.bin");

  switch (ret) {
    case HTTP_UPDATE_FAILED:
      Serial.printf("HTTP_UPDATE_FAILD Error (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
      doc["progress"] = "Failed";
      break;

    case HTTP_UPDATE_NO_UPDATES:
      Serial.println("HTTP_UPDATE_NO_UPDATES");
      doc["progress"] = "No update";
      break;

    case HTTP_UPDATE_OK:
      Serial.println("HTTP_UPDATE_OK");
      doc["progress"] = "Success";
      break;
  }
}

void update_started() {
  Serial.println("CALLBACK:  HTTP update process started");
  start_time = millis();
}

void update_finished() {
  Serial.println("CALLBACK:  HTTP update process finished");
  end_time = millis();
}

void update_progress(int cur, int total) {
  Serial.printf("CALLBACK:  HTTP update process at %d of %d bytes...\n", cur, total);
}

void update_error(int err) {
  Serial.printf("CALLBACK:  HTTP update fatal error code %d\n", err);
}

void status() {
  if (doc.containsKey("progress")) {
    update_time = end_time - start_time;
    doc["command"] = "update";
    doc["update_time"] = update_time;
    publish();
    Serial.println("updated");
    delay(1000);
    if (strcmp(doc["progress"], "Success") == 0) {
      ESP.restart();
    }
  }

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC Address: ");
  Serial.println(macAddress);
  Serial.print("Firmware version: ");
  Serial.println(FIRMWARE_VERSION);
}

void handling(char* topic, byte* payload, unsigned int length) {
  Serial.print("Received message on topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  if (String(topic) == mqtt_topic_sub) {
    if (message == "check") {
      doc["command"] = "checked";
      publish();
    }
  }
  else if (String(topic) == mqtt_self_topic_sub) {
    if (message == "start") {
      update_firmware();
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  handling(topic, payload, length);
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    if (client.connect(macAddress)) {
      Serial.println("connected");
      client.subscribe(mqtt_topic_sub);
      client.subscribe(mqtt_topic_sub_all);
      client.subscribe(mqtt_self_topic_sub);
      status();
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("\nESP-ON");

  // pinMode(LED_1, OUTPUT);
  // pinMode(LED_2, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  ESPhttpUpdate.onStart(update_started);
  ESPhttpUpdate.onEnd(update_finished);
  ESPhttpUpdate.onProgress(update_progress);
  ESPhttpUpdate.onError(update_error);
  ESPhttpUpdate.rebootOnUpdate(false); // remove automatic update
  ESPhttpUpdate.closeConnectionsOnUpdate(false);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      reconnect();
    }
  }
  else {
    setup_wifi();
  }
  client.loop();

  // digitalWrite(LED_1, HIGH);
  // delay(500);
  // digitalWrite(LED_1, LOW);
  // delay(500);
}