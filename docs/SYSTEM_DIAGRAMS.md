# 📊 Project Rakshak: System Diagrams

Project Rakshak's logic and architecture are visualized across four core domains: **Escalation Logic**, **Privacy**, **Emergency Response**, and **System Architecture**.

---

## 🔝 0. Complete System Decision Map
The primary flowchart illustrating high-level project flow from detection to resolution.

```mermaid
flowchart TD
    A([Start]) --> B(User Opens App / Login)
    B --> C[Home Dashboard]
    
    C --> D{Continuous Sensor Monitoring:\nMic, Accelerometer, GPS}
    D --> E((AI Threat Detection System))
    
    E --> F{Threat Detected?}
    F -- No --> D
    F -- Yes --> G{Threat Level?}
    
    G -- Low --> H[Level 1: Check-In Notification]
    H --> I{User Responds?}
    I -- Safe --> D
    I -- No Response --> J[Level 2: Alert Mode]
    
    G -- Medium --> J
    J --> K(Notify Trusted Contacts:\nShare Live Location)
    K --> L[Monitor Situation]
    L --> M{Situation Worsens?}
    
    M -- No --> D
    M -- Yes --> N[Level 3: Emergency Mode Activated]
    
    G -- High --> N
    
    N --> O(Send Alerts to Contacts)
    N --> P(Notify Nearby Users)
    N --> Q(Call Emergency Services)
    N --> R(Record Audio/Video Evidence)
    
    O --> S([Help Arrives / User Safe])
    P --> S
    Q --> S
    R --> S
```

### Logic Breakdown:
1. **Continuous Monitoring**: Always-on sensors feed data into the AI detection engine.
2. **Tiered Assessment**: System classifies events into Level 1 (Low), Level 2 (Medium), or Level 3 (High).
3. **Automated Escalation**: Events naturally move up levels if the situation worsens or if the user fails to respond to check-ins.
4. **Resolution Gateway**: A final "User Safe" state ensures all evidence is saved and rescuers are stood down.

---

## 🔒 1. Privacy Dashboard Workflow
The Privacy Dashboard ensures that users have full control over their sensitive data.

```mermaid
graph TD
    A[Privacy Dashboard Screen] --> B[Microphone Access Log]
    A --> C[Permission Controls]
    A --> D[Encryption Status]
    A --> E[Location Access]
    A --> F[Motion Sensor Access]
    A --> G[Data Controls]
    
    D --> D1[Local Storage: AES-256]
    D --> D2[Network: TLS 1.3]
    D --> D3[End to End Alerts]
    
    G --> G1[Export Data Logs]
    G --> G2[Delete All Data]
    G --> G3[Auto-Delete Evidence]
```

### Key Components:
- **Microphone Access Logs**: Displays the reason for access (e.g., "Keyword detection"), the result (e.g., "No trigger"), and encryption status.
- **Encryption Status**: Highlights the use of **AES-256** for local storage and **TLS 1.3** for network transmissions.
- **Data Controls**: "Right to Be Forgotten" implementation with "Delete All Data" and "Auto-Delete Settings" for evidence (24 hours) and location (30 days).

---

## 🚨 2. Emergency Response Flow (SOS)
This diagram maps the high-stakes journey from a distress signal to a resolved incident.

```mermaid
graph TD
    A[Emergency Triggered] --> B[Emergency Data Package Created]
    B --> C[Location & Audio Encrypted]
    C --> D{Rescue Coordination Engine}
    
    D --> E[Broadcast to Users within 200m]
    D --> F[Send Alerts to Trusted Guardians]
    
    E --> G[Community Responders Arrive]
    F --> H[Guardians Monitor/Call Police]
    
    G --> I[Resolution & Safe Return]
    H --> I
    I --> J[Incident Summary & Evidence Logging]
```

### The Journey:
1. **Trigger**: Emergency triggered via voice signature or manual pulse.
2. **Data Package**: Creation of a secure package containing **GPS Coordinates**, **Threat Type (Screaming/Struggle)**, and **Encrypted Audio**.
3. **Rescue Coordination**: Anonymous broadcast to nearby users within 200m and direct alerts to verified guardians.
4. **Resolution**: Final incident summary and evidence package generation for legal/verification purposes.

---

## ⚙️ 3. Full System Architecture
A deep dive into the background services and ML processing layers.

```mermaid
graph TD
    subgraph Mobile Application
    A[Expo Environment / React Native] --> B[Sensor Services]
    B --> C[Audio / Motion Capture]
    C --> D[TFLite Inference Engine]
    end
    
    subgraph AI Fusion Logic
    D --> E[Voice Anomaly Score]
    D --> F[Motion Anomaly Score]
    E --> G{Score Fusion Engine}
    F --> G
    end
    
    subgraph Cloud Architecture
    G -- High Threat Detected --> H[Django Orchestration Layer]
    H --> I[MongoDB Atlas: Alert Logging]
    H --> J[Daphne / Channels: Notification Dispatch]
    J --> K[Expo Push Services Notification]
    J --> L[Twilio / SMS Fallback]
    end
```

### Functional Layers:
- **Background Services**: Continuous monitoring using low-energy sensor handlers for microphone and motion data.
- **ML Fusion Engine**: A multi-model inference system where Keyword Spoting and Motion Anomaly scores are fused to determine the holistic threat level (LOW/MEDIUM/HIGH).
- **Communication Hub**: Dispatching alerts through **Expo Push (Notifications)** and **Native SMS (Fallback)** when internet connectivity is intermittent.
- **Data Providers**: Real-time sync with MongoDB for user-profiles, contacts, and secure evidence storage.
