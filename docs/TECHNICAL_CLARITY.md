# ⚙️ RAKSHAK: Technical Clarity & Architecture

Project Rakshak's architecture is built on three pillars: **Autonomous Intelligence**, **Serverless Coordination**, and **Secure Data Pipelines**.

---

## 🤖 Machine Learning Engine

### 1. Multi-Model Fusion
The system determines the threat level by fusing scores from two independent TFLite models on-device.

| Model Type | Input Sensor | Target Feature |
| :--- | :--- | :--- |
| **Keyword Spotting** | Microphone | Distress phrase (e.g., "Help", "Bachao") |
| **Motion Anomaly** | Accelerometer | Sudden drops, struggle patterns, or erratic movement |

### 2. Fusion Logic: 60/40 Weighting
The scores are combined in `fusion_logic.py` before triggering the SOS:
- **60% Weight**: Pulse from the Microphone model (high confidence in keyword).
- **40% Weight**: Pulse from the Motion model (high confidence in physical distress).

---

## 📈 Tiered Escalation System

Project Rakshak's core intelligence is mapped into a three-tier response protocol:

### 🥉 Level 1: Low Threat / Check-In Notification
- **Trigger**: Combined anomaly score < 0.45.
- **Action**: A silent "Are you safe?" notification is sent to the user.
- **Escalation**: If the user does not respond within a configurable timeout, the system automatically elevates to **Level 2**.

### 🥈 Level 2: Medium Threat / Alert Mode
- **Trigger**: Combined anomaly score between 0.45 and 0.75 OR no response to Level 1.
- **Action**: 
  - Notifies trusted contacts via silent beacon.
  - Shares live GPS coordinates with guardians.
  - Initiates backend situation monitoring.

### 🥇 Level 3: High Threat / Emergency Mode
- **Trigger**: Combined anomaly score > 0.75 OR situation worsens at Level 2.
- **Action**:
  - Full SOS broadcast to all guardians and nearby community responders (200m).
  - Automated emergency services dispatch.
  - Immediate encryption and recording of audio/video evidence logs.

---

## 📡 API Architecture

The Django backend serves as the orchestration layer for alert coordination.

### Key Endpoints:

- `POST /api/alerts/trigger/`: Creates the initial alert record.
- `POST /api/alerts/verify/`: Escalates the alert and initiates the broadcast.
- `POST /api/alerts/{id}/resolve/`: Clears the alert after a successful rescue.
- `GET /api/alerts/nearby/`: Retrieves alerts within a specific radius (used by the community responder app).

---

## 🗺️ Data Flow: Sensor to Cloud

1. **Acquisition**: RAW PCM (Audio) and $X,Y,Z$ (Motion) captured by Expo-Sensors.
2. **Inference**: On-device TFLite models calculate anomaly probabilities.
3. **Trigger**: If threshold exceeded, `AlertTriggerView` is called with GPS coordinates.
4. **Verification**: After 60s, `AlertVerifyView` initiates notification dispatch.
5. **Broadcast**: Expo-Push Notifications are sent to guardians and nearby users within 200m.

---

## 📈 Security Protocols

- **JWT for Sessions**: Stateless authentication for high-performance scale.
- **TLS 1.3 Encryption**: Secure end-to-end communication with the backend.
- **On-Device Quantization**: Reducing model size for 10ms inference latency on budget mobile devices.

---

> [!TIP]
> **Check Out**: `backend/alerts/views.py` for the implementation of the geospatial broadcast logic.
