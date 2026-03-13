## Context
This project is a high-performance IMU visualization system. The developer is a **Senior Systems Architect**. Ensure all code follows clean architecture principles, avoids unnecessary global variables, and prioritizes non-blocking execution.

## Architectural Constraints
- **Platform:** ESP32-S3 (Dual Core). Use Core 0 for Wi-Fi/Web Server tasks and Core 1 for Sensor Fusion loop if possible.
- **I/O:** Use I2C at **400kHz (Fast Mode)**.
- **Filesystem:** Strictly use **LittleFS**. Do not hardcode HTML/JS as strings in header files.
- **Sensor Fusion:** Do not return raw Pitch/Roll/Yaw to the frontend. Calculate and transmit **Quaternions** `(w, x, y, z)` to avoid gimbal lock in the 3D model.
- **Networking:** Use `ESPAsyncWebServer` for asynchronous handling. Implement a WebSocket endpoint at `/ws`.

## API Protocol
- **Endpoint:** `ws://[device_ip]/ws`
- **Data Format:** JSON
- **Payload Example:** `{"w": 0.98, "x": 0.02, "y": 0.10, "z": -0.15}`

## File Structure
- `src/main.cpp`: Entry point, Wi-Fi init, and sensor loop.
- `src/sensor_fusion.h`: Madgwick/Mahony implementation.
- `data/index.html`: Frontend UI.
- `data/app.js`: Three.js initialization and WebSocket client.
- `platformio.ini`: Dependency management.