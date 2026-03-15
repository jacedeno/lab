# CLAUDE.md - MPU9250 3D Visualization Project

## Project Overview
ESP32-S3 (Seeed XIAO) + MPU-9250 IMU → real-time 3D orientation dashboard via WebSocket + Three.js.

## Quick Reference
- **Board**: `seeed_xiao_esp32s3` (8MB flash, dual-core)
- **Serial port**: `/dev/ttyACM0` (Espressif USB JTAG)
- **WiFi AP**: SSID `NASA-Shuttle-IMU`, pass `12345678`, IP `192.168.4.1`
- **I2C**: SDA=GPIO4, SCL=GPIO5, 400kHz, MPU addr `0x68`
- **Partition**: firmware ~830KB, LittleFS 1.5MB (currently ~615KB used with three.min.js)

## Build & Upload Commands
```bash
pio run                       # Build firmware
pio run -t upload             # Upload firmware only
pio run -t uploadfs           # Upload LittleFS (data/ folder)
pio run -t upload && pio run -t uploadfs  # Both
```

## Reading Serial Output (from Claude Code)
`pio device monitor` doesn't work in non-interactive terminals. Use:
```python
python3 -c "
import serial, time
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.dtr = False; ser.rts = True; time.sleep(0.1)
ser.rts = False; time.sleep(0.1); ser.dtr = True; time.sleep(0.5)
end = time.time() + 10
while time.time() < end:
    line = ser.readline()
    if line:
        print(line.decode('utf-8', errors='replace').strip())
ser.close()
"
```

## Key Files
- `src/main.cpp` — Firmware: WiFi AP, I2C, MPU init, WebSocket broadcast, captive portal DNS
- `src/sensor_fusion.h` — Madgwick filter (header-only, 6-DOF)
- `data/index.html` — Dashboard HTML (loads Three.js locally)
- `data/app.js` — Three.js scene, WebSocket client, rolling charts
- `data/style.css` — Dark theme
- `data/three.min.js` — Three.js r128 (served from LittleFS, NOT CDN)
- `platformio.ini` — Board config + dependencies

## Architecture
- **Core 1**: Sensor task reads MPU-9250 @ 200Hz → Madgwick filter → quaternion
- **Core 0**: WiFi AP + WebSocket broadcast @ 60Hz + DNS captive portal
- **Frontend**: Three.js shuttle model rotated by quaternion, rolling accel/gyro charts

## Current State (2026-03-15)
- WiFi AP + WebSocket + dashboard: **WORKING**
- Captive portal (DNS + connectivity endpoints): **WORKING** — stable on both phone and PC
- Three.js served locally from LittleFS: **WORKING**
- MPU-9250 I2C communication: **NOT WORKING** — `imu.begin()` returns -1, I2C scan finds no devices
- Firmware gracefully skips sensor task if MPU fails (no longer halts)
- All dashboard values show 0 because no sensor data is being sent

## Pending / Next Steps
1. **Fix MPU-9250 I2C wiring** — I2C scan finds nothing. Check:
   - Physical connections (SDA→D4, SCL→D5, VCC→3.3V, GND→GND)
   - Pull-up resistors on SDA/SCL (4.7kΩ to 3.3V if module lacks them)
   - AD0 pin state (GND=0x68, VCC=0x69)
   - Cable continuity with multimeter
2. Once MPU works, sensor data should flow automatically through existing pipeline
3. Optional: add simulated data mode for testing without hardware

## Important Notes
- MPU9250 library MUST be v1.0.2 (Bolder Flight). v5.x is incompatible with Arduino/ESP32.
- ESPAsyncWebServer uses lacamera fork (v3.1.0), NOT the abandoned me-no-dev original.
- Captive portal endpoints must return OS-specific responses (not redirects) to prevent WiFi disconnect.
