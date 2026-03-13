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
    subgraph Physical_Layer ["Layer 1: Physical Hardware & Power"]
        direction TB
        BATT["3.7V LiPo Battery"]
        XIAO["XIAO ESP32-S3"]
        MPU["MPU-9250 IMU Sensor"]
        
        %% Battery Connections
        BATT -- "Positive (+) Red" --> BPAD["B+ Pad (Bottom of XIAO)"]
        BATT -- "Negative (-) Black" --> BNAD["B- Pad (Bottom of XIAO)"]
        
        %% I2C Data & Power Connections
        XIAO -- "3.3V (VCC)" --> MPU
        XIAO -- "GND" --> MPU
        XIAO -- "GPIO 4 (D4 / SDA)" --> MPU
        XIAO -- "GPIO 5 (D5 / SCL)" --> MPU
    end

    subgraph Processing_Layer ["Layer 2: Firmware & Data Processing"]
        direction LR
        LFS[(LittleFS: HTML/JS/3D Assets)]
        Fusion[Sensor Fusion: Madgwick/Mahony]
        WSS[Async WebSocket Server]
        
        XIAO --> LFS
        MPU -- "Raw A/G/M Data" --> Fusion
        Fusion -- "Quaternions (w,x,y,z)" --> WSS
    end

    subgraph Visualization_Layer ["Layer 3: Web Frontend"]
        Browser["Web Browser (macOS/Fedora)"]
        ThreeJS["Three.js Engine (via CDN)"]
        Model3D["3D NASA Shuttle Representation"]
        
        WSS -- "Real-time Stream" --> Browser
        Browser --> ThreeJS
        ThreeJS --> Model3D
    end
