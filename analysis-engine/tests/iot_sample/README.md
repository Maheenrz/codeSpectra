# IoT Sample — Generic 3-Tier Architecture
==========================================

This sample demonstrates cross-layer clone detection on a realistic but
minimal IoT health-monitoring system.  It is deliberately **platform-agnostic**:
the same architecture could be realised with Wear OS, Fitbit, MQTT + Raspberry Pi,
or any other IoT stack without changing how CodeSpectra detects the clones.

## Architecture

```
device_layer/HealthSensorService.kt
    ↓  (Wearable data path / BLE / MQTT)
bridge_layer/PhoneGatewayService.kt
    ↓  (HTTP / cloud sync)
cloud_layer/health_api_server.js
```

## Intentional cross-layer clone pairs

| Canonical name      | Device layer            | Bridge layer              | Cloud layer              |
|---------------------|-------------------------|---------------------------|--------------------------|
| `getHeartRate`      | `getHeartRate()`        | `getHeartRate()`          | `GET /heart-rate`        |
| `getUserProfile`    | `getUserProfile()`      | `getUserProfile()`        | `GET /user/profile`      |
| `postActivityLog`   | `postActivityLog()`     | `postActivityLog()`       | `POST /activity/log`     |
| `getSleepData`      | `getSleepData()`        | `getSleepData()`          | `GET /sleep/data`        |

The synonym normaliser will additionally bridge:
- `fetchHeartRate()` (bridge) → canonical `getHeartRate` → matches device + cloud

## How to run the cross-layer test

```bash
cd analysis-engine
python -m pytest tests/test_cross_layer_detection.py -v
```

## Why these three files?

- **HealthSensorService.kt** — detected as `DEVICE_LAYER` because it imports
  `com.google.android.gms.wearable` (Wear OS signal).  Swap this for any
  device SDK and the layer detection still fires.
- **PhoneGatewayService.kt** — detected as `BRIDGE_LAYER` via `DataClient.OnDataChangedListener`.
  Could equally be a Python MQTT gateway or a Node.js BLE proxy.
- **health_api_server.js** — detected as `CLOUD_LAYER` via Express route definitions.
