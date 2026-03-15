#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <DNSServer.h>
#include <LittleFS.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include "MPU9250.h"
#include "sensor_fusion.h"

// --- Pin and I2C config ---
static constexpr int PIN_SDA = 4;
static constexpr int PIN_SCL = 5;
static constexpr uint32_t I2C_FREQ = 400000;
static constexpr uint8_t MPU_ADDR = 0x68;

// --- WiFi AP config ---
static const char* AP_SSID = "NASA-Shuttle-IMU";
static const char* AP_PASS = "12345678";

// --- Timing ---
static constexpr float SENSOR_HZ = 200.0f;
static constexpr uint32_t SENSOR_PERIOD_MS = 1000 / (uint32_t)SENSOR_HZ; // 5ms
static constexpr float WS_HZ = 60.0f;
static constexpr uint32_t WS_PERIOD_MS = 1000 / (uint32_t)WS_HZ;        // 16ms

// --- IMU state ---
static bool mpuReady = false;

// --- Shared sensor data ---
struct SensorData {
    float w, x, y, z;       // quaternion
    float ax, ay, az;        // accel (m/s^2)
    float gx, gy, gz;        // gyro (rad/s)
    bool valid;
};

static SensorData sensorData = {};
static SemaphoreHandle_t dataMutex;

// --- Hardware ---
static MPU9250 imu(Wire, MPU_ADDR);
static MadgwickFilter filter(0.1f, SENSOR_HZ);

// --- Network ---
static DNSServer dnsServer;
static AsyncWebServer server(80);
static AsyncWebSocket ws("/ws");

// --- Sensor task (Core 1, 200 Hz) ---
void sensorTask(void* param) {
    TickType_t lastWake = xTaskGetTickCount();

    for (;;) {
        if (imu.readSensor() > 0) {
            float ax = imu.getAccelX_mss();
            float ay = imu.getAccelY_mss();
            float az = imu.getAccelZ_mss();
            float gx = imu.getGyroX_rads();
            float gy = imu.getGyroY_rads();
            float gz = imu.getGyroZ_rads();

            filter.update(gx, gy, gz, ax, ay, az);

            if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(1)) == pdTRUE) {
                sensorData.w  = filter.w();
                sensorData.x  = filter.x();
                sensorData.y  = filter.y();
                sensorData.z  = filter.z();
                sensorData.ax = ax;
                sensorData.ay = ay;
                sensorData.az = az;
                sensorData.gx = gx;
                sensorData.gy = gy;
                sensorData.gz = gz;
                sensorData.valid = true;
                xSemaphoreGive(dataMutex);
            }
        }

        vTaskDelayUntil(&lastWake, pdMS_TO_TICKS(SENSOR_PERIOD_MS));
    }
}

// --- WebSocket event handler ---
void onWsEvent(AsyncWebSocket* server, AsyncWebSocketClient* client,
               AwsEventType type, void* arg, uint8_t* data, size_t len) {
    if (type == WS_EVT_CONNECT) {
        Serial.printf("[WS] Client #%u connected\n", client->id());
    } else if (type == WS_EVT_DISCONNECT) {
        Serial.printf("[WS] Client #%u disconnected\n", client->id());
    }
}

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}
    Serial.println("\n[BOOT] ESP32-S3 MPU-9250 Dashboard");

    // I2C
    Wire.begin(PIN_SDA, PIN_SCL);
    Wire.setClock(I2C_FREQ);

    // I2C scan
    Serial.println("[I2C] Scanning...");
    for (uint8_t addr = 1; addr < 127; addr++) {
        Wire.beginTransmission(addr);
        if (Wire.endTransmission() == 0) {
            Serial.printf("[I2C] Device found at 0x%02X\n", addr);
        }
    }

    // MPU-9250 init
    int status = imu.begin();
    if (status < 0) {
        Serial.printf("[MPU] Init FAILED (status %d). WiFi will start without sensor.\n", status);
    } else {
        Serial.println("[MPU] Init OK");
        imu.setAccelRange(MPU9250::ACCEL_RANGE_8G);
        imu.setGyroRange(MPU9250::GYRO_RANGE_500DPS);
        imu.setDlpfBandwidth(MPU9250::DLPF_BANDWIDTH_92HZ);
        imu.setSrd(4); // 1000/(4+1) = 200 Hz
        mpuReady = true;
    }

    // LittleFS
    if (!LittleFS.begin(true)) {
        Serial.println("[FS] LittleFS mount FAILED. No web UI.");
    } else {
        Serial.println("[FS] LittleFS mounted");
    }

    // WiFi AP
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    delay(100);
    Serial.printf("[WiFi] AP started: %s @ %s\n", AP_SSID,
                  WiFi.softAPIP().toString().c_str());

    // Captive portal DNS: resolve all domains to our IP
    dnsServer.start(53, "*", WiFi.softAPIP());
    Serial.println("[DNS] Captive portal DNS started");

    // WebSocket
    ws.onEvent(onWsEvent);
    server.addHandler(&ws);

    // Captive portal: respond what each OS expects so they think there IS internet
    // Android: expects HTTP 204
    server.on("/generate_204", HTTP_GET, [](AsyncWebServerRequest *r) {
        r->send(204);
    });
    // Android alternate
    server.on("/gen_204", HTTP_GET, [](AsyncWebServerRequest *r) {
        r->send(204);
    });
    // Windows: expects "Microsoft Connect Test" with 200
    server.on("/connecttest.txt", HTTP_GET, [](AsyncWebServerRequest *r) {
        r->send(200, "text/plain", "Microsoft Connect Test");
    });
    // Windows NCSI
    server.on("/ncsi.txt", HTTP_GET, [](AsyncWebServerRequest *r) {
        r->send(200, "text/plain", "Microsoft NCSI");
    });
    // Apple: expects 200 with "Success"
    server.on("/hotspot-detect.html", HTTP_GET, [](AsyncWebServerRequest *r) {
        r->send(200, "text/html", "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>");
    });
    server.on("/library/test/success.html", HTTP_GET, [](AsyncWebServerRequest *r) {
        r->send(200, "text/html", "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>");
    });
    // Firefox
    server.on("/canonical.html", HTTP_GET, [](AsyncWebServerRequest *r) {
        r->send(200, "text/html", "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>");
    });
    server.on("/success.txt", HTTP_GET, [](AsyncWebServerRequest *r) {
        r->send(200, "text/plain", "success\n");
    });

    // Serve static files from LittleFS
    server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");

    server.begin();
    Serial.println("[HTTP] Server started on port 80");

    // Mutex
    dataMutex = xSemaphoreCreateMutex();

    // Sensor task on Core 1 (only if MPU is ready)
    if (mpuReady) {
        TaskHandle_t sensorHandle = nullptr;
        xTaskCreatePinnedToCore(sensorTask, "SensorTask", 8192, nullptr, 2,
                                &sensorHandle, 1);
        Serial.println("[TASK] Sensor task started on Core 1");
    } else {
        Serial.println("[TASK] Sensor task SKIPPED (no MPU)");
    }
}

void loop() {
    dnsServer.processNextRequest();

    static uint32_t lastWsBroadcast = 0;

    uint32_t now = millis();
    if (now - lastWsBroadcast >= WS_PERIOD_MS) {
        lastWsBroadcast = now;

        ws.cleanupClients();

        if (ws.count() > 0) {
            SensorData d;
            bool got = false;

            if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(1)) == pdTRUE) {
                d = sensorData;
                got = sensorData.valid;
                xSemaphoreGive(dataMutex);
            }

            if (got) {
                JsonDocument doc;
                doc["w"]  = serialized(String(d.w, 4));
                doc["x"]  = serialized(String(d.x, 4));
                doc["y"]  = serialized(String(d.y, 4));
                doc["z"]  = serialized(String(d.z, 4));
                doc["ax"] = serialized(String(d.ax, 2));
                doc["ay"] = serialized(String(d.ay, 2));
                doc["az"] = serialized(String(d.az, 2));
                doc["gx"] = serialized(String(d.gx, 3));
                doc["gy"] = serialized(String(d.gy, 3));
                doc["gz"] = serialized(String(d.gz, 3));

                char buf[256];
                size_t len = serializeJson(doc, buf, sizeof(buf));
                ws.textAll(buf, len);
            }
        }
    }

    delay(1);
}
