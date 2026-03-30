# 💎 RAKSHAK: Implementation Quality & Reliability

The core of Project Rakshak is built to be resilient, secure, and privacy-conscious. This document explores the engineering choices that ensure high-quality delivery.

---

## 🔒 Security Architecture

### 1. Data at Rest (AES-256)
- Most emergency data is stored on-device to minimize cloud exposure.
- Sensitive logs, including voice-signatures and location breadcrumbs, are encrypted using **AES-256** with keys stored in the device's secure hardware (iOS Keychain / Android Keystore).

### 2. Data in Transit (TLS 1.3)
- All API communication with the Django backend is enforced via **TLS 1.3** to prevent Man-in-the-Middle (MITM) attacks.

### 3. Authentication & Authorization
- Robust **JWT (JSON Web Token)** implementation for session management.
- Permission-based access controls to sensitive endpoints like `/alerts/trigger/` and `/profile/update/`.

---

## 🚀 Reliability & Edge Cases

### 1. Offline Protocol (Native Fallback)
When internet connectivity is lost or the API is unreachable:
- Rakshak automatically switches to **Native SMS Fallback**.
- A direct message with a Google Maps location link is sent to the registered guardian using the device's cellular network.

### 2. False Alarm Mitigation (The Dead-Man's Switch)
To prevent accidental SOS triggers:
- A **60-second countdown** is initiated upon detection.
- The user can cancel the alert at any time during this window.
- If the timer expires without cancellation, the alert is automatically escalated to "ACTIVE" and broadcasted.

### 3. Battery-Aware Background Monitoring
- Sensor acquisition (Microphone/Motion) is optimized for low power consumption.
- On-device inference is quantized for speed and efficiency, ensuring the app remains lightweight even during long standby periods.

---

## 🏗️ Code Patterns

- **Clean Architecture**: Separation of concerns between UI (Mobile), Business Logic (Alert Coordination), and Data (MongoDB/SQLite).
- **Asynchronous Processing**: Background tasks (notifications, geo-queries) are handled asynchronously to maintain UI responsiveness.
- **Unit Testing**: Core logic like `fusion_logic.py` and API endpoints are backed by automated tests to ensure zero regressions.

---

> [!IMPORTANT]
> **Privacy First**: We do not store raw audio or video on the cloud unless explicitly triggered by an Emergency SOS after the 60s verification window.
