#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>

#define ssid "Ekarema"
#define password "Sang5453"
#define mqtt_server "mqtt.eclipseprojects.io"  //Alamat broker MQTT
#define mqtt_topic1 "OTAUpdate/klien/cekESP"
#define mqtt_topic2 "OTAUpdate/klien/updateTunggal"

#define FIRMWARE_VERSION "0.1"

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  WiFi.mode(WIFI_STA);
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
}

void update_firmware() {
  Serial.println(F("Update start now!"));

  t_httpUpdate_return ret = ESPhttpUpdate.update(espClient, "192.168.246.27", 3000, "/firmware/httpUpdateNew.bin");

  switch (ret) {
    case HTTP_UPDATE_FAILED:
      Serial.printf("HTTP_UPDATE_FAILD Error (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
      Serial.println(F("Retry in 10secs!"));
      delay(10000); // Wait 10secs
      break;

    case HTTP_UPDATE_NO_UPDATES:
      Serial.println("HTTP_UPDATE_NO_UPDATES");
      break;

    case HTTP_UPDATE_OK:
      Serial.println("HTTP_UPDATE_OK");
      delay(1000); // Wait a second and restart
      ESP.restart();
      break;
  }
}

void update_started() {
  Serial.println("CALLBACK:  HTTP update process started");
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

void handling(char* topic, byte* payload, unsigned int length) {
  Serial.print("Received message on topic: ");
  Serial.println(topic);
  Serial.print("Message: ");

  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  //<------------------------->
  if (topic == mqtt_topic1) {
    bool y = true
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  handling(topic, payload, length);
}

void status() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  char macAddress[18]; // 18 karakter untuk MAC Address (6 byte * 3 karakter + 5 tanda ":" + 1 karakter null-terminator)
  snprintf(macAddress, sizeof(macAddress), "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC Address: ");
  Serial.println(macAddress);
  Serial.print("Firmware version: ");
  Serial.println(FIRMWARE_VERSION);
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    if (client.connect("OTAUpdateMqttESP8266Client")) {
      Serial.println("connected");
      client.subscribe(mqtt_topic1);
      client.subscribe(mqtt_topic2);
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
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  ESPhttpUpdate.onStart(update_started);
  ESPhttpUpdate.onEnd(update_finished);
  ESPhttpUpdate.onProgress(update_progress);
  ESPhttpUpdate.onError(update_error);
  ESPhttpUpdate.rebootOnUpdate(false); // remove automatic update

  status();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();
}