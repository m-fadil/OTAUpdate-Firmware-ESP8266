#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>
#include <ArduinoJson.h>
#include <ESP_EEPROM.h>
#include <RTClib.h>

#define FIRMWARE_VERSION "0.2"
#define ssid "DESKTOP"
#define password "TmzXgd4Z"
#define mqtt_server "4.145.89.184"
#define mqtt_port 1883
#define mqtt_topic_sub "OTAUpdate/esp"
#define mqtt_topic_pub "OTAUpdate/klien"
#define espId "ESP-Sensor_Suhu"
#define LED_1 2
char macAddress[18];
char mqtt_self_topic_sub[35];

unsigned long reconnectMillis = 0;

struct DataTime {
  byte hour = 0;
  byte minute = 0;
  byte second = 0;
};

DynamicJsonDocument doc(1024);
String JSONPayload;

WiFiClient espClient;
PubSubClient client(espClient);

RTC_DS1307 rtc;

void setup_wifi() {
  WiFi.mode(WIFI_STA);
  digitalWrite(LED_1, LOW);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  digitalWrite(LED_1, HIGH);
  uint8_t mac[6];
  WiFi.macAddress(mac);
  sprintf(macAddress, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  sprintf(mqtt_self_topic_sub, "%s/%s", mqtt_topic_sub, macAddress);
  
  doc["mac"] = macAddress;
}

void saveDateTimeToEEPROM(DataTime dataTime) {
  DateTime now = rtc.now();
  dataTime.hour = now.hour();
  dataTime.minute = now.minute();
  dataTime.second = now.second();
  EEPROM.put(0, dataTime);
  boolean ok = EEPROM.commit();
  Serial.println((ok) ? "commit OK" : "Commit failed");
}

void publish() {
  JSONPayload = "";
  serializeJson(doc, JSONPayload);
  client.publish(mqtt_topic_pub, JSONPayload.c_str());
}

void update_firmware() {
  Serial.println(F("Update start now!"));
  doc["command"] = "update";
  doc["progress"] = "updating";
  doc["update_time_start"] = nullptr;
  doc["update_time_end"] = nullptr;
  publish();

  t_httpUpdate_return ret = ESPhttpUpdate.update(espClient, "4.145.89.184", 3000, "/firmware/firmware_update.bin");

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

  DataTime startTime;
  saveDateTimeToEEPROM(startTime);
}

void update_finished() {
  Serial.println("CALLBACK:  HTTP update process finished");
}

void update_progress(int cur, int total) {
  Serial.printf("CALLBACK:  HTTP update process at %d of %d bytes...\n", cur, total);
}

void update_error(int err) {
  Serial.printf("CALLBACK:  HTTP update fatal error code %d\n", err);
}

void status() {
  if (doc["progress"] != nullptr) {
    doc["command"] = "update";
    publish();
    Serial.println("updated");

    delay(1000);
    if (doc["progress"] == "Success") {
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
    else if (message == "start") {
      update_firmware();
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

void reconnect_mqtt() {
  Serial.println("Attempting MQTT connection...");
  if (client.connect(macAddress)) {
    Serial.println("connected");
    client.subscribe(mqtt_topic_sub);
    client.subscribe(mqtt_self_topic_sub);
    status();
  } else {
    Serial.print("failed, rc=");
    Serial.print(client.state());
    Serial.println(" try again in 5 seconds");
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("\nESP-ON");

  doc["espId"] = espId;
  doc["version"] = FIRMWARE_VERSION;
  doc["mac"] = nullptr;
  doc["command"] = nullptr;
  doc["progress"] = nullptr;
  doc["update_time_start"] = nullptr;
  doc["update_time_end"] = nullptr;

  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }

  EEPROM.begin(16);
  
  DataTime startTime;
  EEPROM.get(0, startTime);
  if (startTime.hour != 0) {
    DateTime now = rtc.now();
    String st = String(startTime.hour) + ":" + String(startTime.minute) + ":" + String(startTime.second);
    String et = String(now.hour()) + ":" + String(now.minute()) + ":" + String(now.second());
    Serial.println("Update start: " + st);
    Serial.println("Update end: " + et);

    doc["progress"] = "finished";
    doc["update_time_start"] = st;
    doc["update_time_end"] = et;

    EEPROM.put(0, 0);
    boolean ok = EEPROM.commit();
    Serial.println((ok) ? "commit 0 OK" : "Commit failed");
  }

  pinMode(LED_1, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  ESPhttpUpdate.onStart(update_started);
  ESPhttpUpdate.onEnd(update_finished);
  ESPhttpUpdate.onProgress(update_progress);
  ESPhttpUpdate.onError(update_error);
  ESPhttpUpdate.rebootOnUpdate(false);
  ESPhttpUpdate.closeConnectionsOnUpdate(false);

  doc["espId"] = espId;
  doc["mac"] = macAddress;
  doc["version"] = FIRMWARE_VERSION;
  doc["command"] = nullptr;
  doc["progress"] = nullptr;
  doc["update_time"] = nullptr;
}

void loop() {
  unsigned long currentMillis = millis();
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }

  if (!client.connected() && (currentMillis - reconnectMillis >= 5000)) {
    reconnect_mqtt();
    reconnectMillis = currentMillis;
  }
  client.loop();

  // digitalWrite(LED_1, HIGH);
  // delay(1000);
  // digitalWrite(LED_1, LOW);
  // delay(1000);
}