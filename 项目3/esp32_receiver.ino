// main.ino (或 main.cpp)

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi配置
const char* ssid = "YOUR_WIFI_SSID";        // 替换为你的WiFi名称
const char* password = "YOUR_WIFI_PASSWORD";    // 替换为你的WiFi密码

// API服务器配置
const char* apiHost = "YOUR_API_SERVER_IP"; // 替换为运行Python API的电脑的IP地址
const int apiPort = 5000;                   // Python API的端口，默认为5000
const char* apiEndpoint = "/api/audio/esp32/data"; // 获取数据的API接口

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("
WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String serverPath = String("http://") + apiHost + ":" + apiPort + apiEndpoint;

    Serial.println("\nMaking HTTP GET request to: ");
    Serial.println(serverPath);

    http.begin(serverPath);

    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String payload = http.getString();
      Serial.println(payload);

      // 解析JSON
      StaticJsonDocument<200> doc; // 根据JSON大小调整容量
      DeserializationError error = deserializeJson(doc, payload);

      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
      }

      int bpm = doc["bpm"];
      int db = doc["db"];
      int hz = doc["hz"];
      bool recording = doc["recording"];
      long timestamp = doc["timestamp"];

      Serial.print("BPM: ");
      Serial.println(bpm);
      Serial.print("dB: ");
      Serial.println(db);
      Serial.print("Hz: ");
      Serial.println(hz);
      Serial.print("Recording: ");
      Serial.println(recording ? "Yes" : "No");
      Serial.print("Timestamp: ");
      Serial.println(timestamp);

    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }
  else {
    Serial.println("WiFi Disconnected");
  }
  delay(2000); // 每2秒获取一次数据
}


