# XIAO-S3 NASA Shuttle Orientation Dashboard

A high-performance IIoT visualization project utilizing the **Seeed Studio XIAO ESP32-S3** and the **MPU-9250** (9-DOF) sensor. This system provides real-time 3D orientation tracking (NASA Shuttle/Rocketship) in a web browser via WebSockets and Three.js.

## 🚀 Overview

- **Real-time Sensor Fusion:** Implements Madgwick/Mahony filters to convert raw IMU data into stable Quaternions.
- **Low-Latency Communication:** Uses asynchronous WebSockets to stream orientation data at 60Hz.
- **Decoupled Frontend:** A Three.js-based dashboard hosted on **LittleFS** and served directly from the ESP32.
- **Autonomous Power:** Integrated LiPo battery management for a completely wireless 3D-printed model.

## 🛠 Technical Stack

- **Hardware:** Seeed Studio XIAO ESP32-S3 (Dual-core, Wi-Fi/BT, LiPo charging).
- **Sensor:** InvenSense MPU-9250 (I2C @ 400kHz).
- **Environment:** PlatformIO / VS Code.
- **Firmware:** C++ with `ESPAsyncWebServer` and `Bolder Flight Systems MPU9250`.
- **Frontend:** HTML5, CSS3, JavaScript (Three.js), WebSockets.

## 🔌 Hardware Wiring (I2C)

| XIAO ESP32-S3 | MPU-9250 Pin | Description |
| :--- | :--- | :--- |
| **3.3V** | VCC | Power Supply |
| **GND** | GND | Common Ground |
| **D4 (GPIO 4)** | SDA | I2C Serial Data |
| **D5 (GPIO 5)** | SCL | I2C Serial Clock |
| **B+ (Pad)** | LiPo Red (+) | Battery Positive |
| **B- (Pad)** | LiPo Black (-) | Battery Negative |

## 🏗 System Architecture

```mermaid
graph TD
    subgraph Hardware ["Physical Layer"]
        BATT[LiPo Battery 3.7V] --> XIAO[XIAO ESP32-S3]
        XIAO <-->|I2C 400kHz| MPU[MPU-9250 IMU]
    end

    subgraph Firmware ["ESP32 Logic (PlatformIO)"]
        Filter[Sensor Fusion Filter] --> JSON[JSON Serializer]
        JSON --> WS[Async WebSocket Server]
    end

    subgraph Storage ["Filesystem (LittleFS)"]
        HTML[index.html]
        Model[shuttle.gltf]
    end

    subgraph View ["Frontend (Browser)"]
        Three[Three.js Engine] --> Render[3D NASA Shuttle]
        WS -.->|Quaternions| Three
    end
