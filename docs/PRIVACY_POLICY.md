# 🛡️ Privacy Policy & Data Handling

*Effective Date: Today*

Project RAKSHAK is built on the fundamental principle that safety should not compromise privacy. This document deeply explains the lifecycle of user data from the device sensor to the cloud.

---

## 1. Zero-Trust Data Lifecycle

### Sensor Acquisition (The Edge)
RAKSHAK actively utilizes your device's microphone and accelerometer. However, **this data never leaves your device by default**. 
- The microphone buffer is analyzed locally by a quantized **TensorFlow Lite (TFLite)** model running inside the React Native thread.
- Raw PCM audio data is continuously overwritten in a temporary circular buffer and is immediately discarded if the model probability scores do not exceed the threat threshold.

### Escalation & Transmission
Only when a **Level 3 High Threat** is detected (either via keyword match or manual SOS) does data transmission begin:
- A snapshot of the audio snippet (evidence) is captured.
- This evidence is encrypted on the device using symmetric keys before transmission.

---

## 2. Cryptographic Privacy (Data at Rest)

All user profiles, contact lists, and metadata are housed securely inside an isolated **MongoDB Atlas** cluster. 
- The database enforces strict Role-Based Access Controls (RBAC) preventing unauthorized querying.
- Any generated media (audio signatures, video logs) are strictly **AES-256 encrypted** prior to storage. Without the environment-level decryption keys on the backend, physical access to the server disk yields only indecipherable ciphertexts.

---

## 3. The "Right to be Forgotten" (Data Deletion)

We strictly adhere to data portability and deletion doctrines (such as GDPR/CCPA concepts).
- Users own their data telemetry completely.
- A programmatic route (`DELETE /api/evidence/<id>`) permanently drops evidence blobs and pulls them out of the AWS S3/local file systems instantly.
- **Auto-Deletion Policies**: Emergency alerts and associated tracking data automatically expire and self-destruct after 30 days of inactivity to prevent data hoarding.

---

## 4. Anonymized Community Pings

When you trigger an alert, a community broadcast is emitted to users within a **200-meter radius**.
- **What is sent**: A boolean flag (`alert_nearby: true`) and a generalized spatial zone.
- **What is NOT sent**: Your name, phone number, exact GPS coordinates, or the audio snippet. The community app only points them in the general direction without deanonymizing the victim.

---

## 5. Third-Parties and Auditing

RAKSHAK does not sell, trade, or transfer any Personally Identifiable Information (PII). Internal systems are mapped dynamically so that even database administrators cannot piece together an identity from the raw hashed logs.
