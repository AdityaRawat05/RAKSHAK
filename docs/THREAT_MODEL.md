# 🚨 Threat Modeling - RAKSHAK

This document defines the comprehensive threat model for the Rakshak platform. When engineering a life-saving safety application, standard operational vulnerabilities (like XSS or CSRF) pale in comparison to physical and privacy-based risks. 

Our threat model identifies six core vectors and details the systemic defenses engineered to neutralize them.

---

## 1. Physical Device Compromise (The Attacker Takes the Phone)
**The Scenario**: An assailant forcibly confiscates the victim's smartphone immediately after the SOS is triggered, attempting to cancel the alert or delete evidence.
- **Vulnerability**: Unlocked screen access or forced biometric unlocking.
- **The Defense (Irreversible Escalation)**: 
  1. Once the 60-second "Dead-Man's Switch" expires (or is bypassed), the alert is marked `ACTIVE` on the cloud. 
  2. The mobile client *cannot* locally cancel an `ACTIVE` alert. Only recognized backend resolutions by verified authorities or pre-approved contacts can stand down the system.
  3. All local evidence files (audio logs) recorded automatically by the device are **AES-256 Encrypted**. The assailant cannot open the filesystem and play or delete the recordings without the decryption key stored separately on the server.

---

## 2. PII Deanonymization (The "Stalker" Vector)
**The Scenario**: A bad actor registers on the app purely to scrape the `/api/alerts/nearby/` endpoint, mapping out the precise GPS locations of vulnerable victims.
- **Vulnerability**: Precise Floating-Point Geospatial data leakage.
- **The Defense (Spatial Fuzzing)**: 
  1. The backend implements a "Haversine Fuzzing" strategy. 
  2. Raw `latitude` and `longitude` are dropped from the community response payload.
  3. Instead, the endpoint returns a generalized "Zone" (e.g., "Alert within your bounding box") and strips the victim's `User ID`, `Name`, and `Phone Number`. The community responder only knows **someone** nearby needs help, preventing stalker tracking.

---

## 3. Fake Alert Flooding (Denial of Service)
**The Scenario**: A coordinated botnet or malicious user triggers thousands of false SOS alerts to overwhelm the MongoDB database or panic the community.
- **Vulnerability**: Open REST API triggers.
- **The Defense (Rate Limiting & Triage)**:
  1. **Strict Throttling**: The `/alerts/trigger/` endpoint uses a Token Bucket algorithm limiting users to **10 requests per minute**. Violations result in IP/Account temporary blacklisting.
  2. **Reputation Dropping**: The AI Fusion Engine tags incoming alerts with a confidence score. If a user habitually generates 0.01 confidence "threats", the system algorithmically deprioritizes their community broadcasts.

---

## 4. WebSocket Hijacking
**The Scenario**: An attacker intercepts the WebSocket connection URL used for live victim tracking and listens in on the latitude/longitude data stream.
- **Vulnerability**: Unauthenticated Socket Connections.
- **The Defense (Handshake Validation)**:
  1. The Django Channels router requires a JWT token passed during the physical handshake (`ws://domain/ws/location/?token=XYZ`).
  2. The consumer decrypts the JWT. If the user ID pulling the stream does not belong to the victim's verified `Trusted Contacts` array, the connection is instantly rejected at the ASGI layer with an `Access Denied` fatal close code.

---

## 5. Brute Force Credential Targeting
**The Scenario**: Standard automated credential stuffing against user accounts trying to expose their designated guardians or tracked locations.
- **Vulnerability**: Weak passwords, standard authentication flow.
- **The Defense (Cryptographic Hashing)**:
  1. Passwords use BCrypt variable-cost hashing with salt. The computational cost prevents Rainbow Table analysis.
  2. Global `5 requests/min` login limit per IP.

---

## 6. Server Breach (Data Exfiltration)
**The Scenario**: A zero-day exploit grants an attacker root bash access to the backend Django servers.
- **Vulnerability**: Cloud infrastructure compromise.
- **The Defense (Data at Rest Encryption)**:
  1. The attacker would see `.enc` files in `MEDIA_ROOT`. Because the `AES_ENCRYPTION_KEY` resides strictly in the in-memory environment variables (which vanish if the process dies or through strict `.env` file permission locking), the files cannot be read.
  2. The MongoDB cluster (`mongodb+srv`) resides on a separate network entirely, protected by strict IP Whitelisting (`0.0.0.0/0` is only used for local dev).
