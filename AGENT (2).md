# AGENT.md — RAKSHAK: AI-Powered Proactive Women Safety System
> This file defines the role, responsibilities, context, and instructions for every AI agent working on this project.
> Each agent must read only its own section + the Shared Context before starting work.
> ⚠️ NO PAID CLOUD SERVICES — uses MongoDB Atlas Free Tier (M0, 512MB), everything else is local or free.

---

## 📌 PROJECT OVERVIEW

**Project Name:** RAKSHAK — AI-Powered Proactive Women Safety System
**Team:** TechX (Hack-O-Holic 4.0)
**Institution:** Graphic Era Hill University, Dehradun

RAKSHAK is a hands-free, always-on women safety mobile app that uses on-device AI to detect threats automatically via sensor fusion (voice keyword + motion + GPS), then triggers a multi-stage alert to trusted contacts and nearby community users — without the victim needing to do anything manually.

---

## 🔗 SHARED CONTEXT (All Agents Must Read This)

### Tech Stack (Free Only)
| Layer | Technology | Cost |
|---|---|---|
| Mobile App | React Native (Expo SDK) | Free |
| Backend | Django + Django REST Framework | Free |
| Database | MongoDB Atlas Free Tier (M0 — 512MB) | Free |
| DB Driver | PyMongo (direct driver, no ORM) | Free |
| File Storage | Local filesystem (`MEDIA_ROOT`) | Free |
| AI/ML | TensorFlow Lite (on-device) | Free |
| Real-Time | Django Channels + Redis (local) | Free |
| Push Notifications | Expo Push Notification Service | Free |
| Maps | OpenStreetMap via `react-native-maps` | Free |
| Security | JWT Auth, Fernet AES-256 (`cryptography` lib) | Free |
| Dev Tunneling | ngrok free tier | Free |

### ❌ Do NOT Use (Paid Services — Removed)
- ~~AWS S3~~ → Use local `MEDIA_ROOT` folder
- ~~Firebase Storage / Firestore / FCM~~ → Expo Push + local storage + MongoDB Atlas
- ~~Google Maps SDK (billed)~~ → OpenStreetMap (free, no API key)
- ~~PostgreSQL hosted~~ → MongoDB Atlas free M0 cluster
- ~~AWS EC2 / GCP / Heroku paid~~ → localhost + ngrok for demo
- ~~Sentry paid~~ → Django file-based logging

### MongoDB Atlas Free Tier Notes
- Sign up: https://www.mongodb.com/cloud/atlas/register (no credit card needed)
- Create a **FREE M0 cluster** (512MB, shared)
- Network Access → Add IP: `0.0.0.0/0` (for dev)
- Connection string format:
  `mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/rakshak_db?retryWrites=true&w=majority`
- Store in `.env` as `MONGODB_URI`

### MongoDB Collections
```
rakshak_db/
├── users               # profile, expo_push_token, location {lat, lng}
├── trusted_contacts    # per-user emergency contacts
├── distress_keywords   # voice keyword metadata (file path, language)
├── alerts              # alert lifecycle documents
├── evidence            # evidence metadata (file path, encrypted flag)
└── alert_logs          # event log per alert
```

### Core Alert Workflow
```
Background sensors running (mic, gyroscope, GPS)
        ↓
Anomaly detected (keyword / abnormal motion)
        ↓
Low Risk  → Silent check-in to user (confirm / cancel within 10s)
        ↓
No response OR High Risk → Multi-sensor verification
        ↓
Alert confirmed →
    1. Notify trusted contacts via Expo Push (free)
    2. Broadcast anonymous alert to nearby users (Haversine query on Atlas)
    3. Begin AES-256 encrypted audio/video — saved to local device + backend MEDIA_ROOT
    4. Log incident to MongoDB Atlas for legal evidence
```

### Folder Structure (Monorepo)
```
rakshak/
├── mobile/          # Expo (React Native) app
├── backend/         # Django REST API
├── ml/              # TensorFlow Lite model training & export
├── docs/            # Documentation
└── AGENT.md         # This file
```

### Rules Every Agent Must Follow
- Never hardcode secrets or API keys — use `.env` files only.
- All API endpoints must require JWT authentication (except register/login).
- Evidence audio/video must be AES-256 encrypted before saving to disk.
- Write unit tests for every module.
- Document every function/class with comments.
- Follow REST conventions: correct HTTP methods, status codes, error messages.
- No paid services — MongoDB Atlas M0 free tier is the only external service allowed.
- Communicate assumptions in code comments or `NOTES.md`.

---

## 👤 AGENT 1 — Mobile App Agent (Expo + React Native)

### Role
Build the cross-platform mobile application using Expo SDK for Android and iOS. Use only free libraries and the Expo Push Notification Service (no Firebase).

### ⚠️ Expo-Specific Rules
- Use **Expo managed workflow** as the base.
- Use `expo-dev-client` for development builds with custom native modules.
- All native permissions declared in `app.json` under the `expo` key.
- Use **EAS Build free tier** (`eas build --profile development --platform android`) for APK.
- Push notifications via **Expo Push Notification Service** (free — no Firebase needed).
- Maps via **OpenStreetMap** with `react-native-maps` (free — no Google billing or API key).

### Responsibilities
- Initialize: `npx create-expo-app rakshak-mobile --template blank-typescript`
- Set up folder structure: `app/`, `components/`, `services/`, `hooks/`, `store/`, `constants/`, `tasks/`
- Use **Expo Router** for file-based navigation
- Build all screens: Login, Register, Home, Emergency Overlay, Contacts, Settings, Keyword Recording
- Build distress keyword recording screen using `expo-av`
- Implement trusted contacts management using `expo-contacts` + manual entry
- Build background task service using `expo-task-manager` + `expo-background-fetch`
- Integrate **OpenStreetMap** using `react-native-maps` with OSM tile template
- Handle push notifications using `expo-notifications` (register Expo push token → send to backend)
- Implement emergency UI overlay
- Declare all permissions in `app.json`
- Store JWT tokens in `expo-secure-store` (NOT AsyncStorage)
- Connect to backend APIs using `axios`

### Key Files to Create
```
mobile/
├── app/
│   ├── (auth)/
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (tabs)/
│   │   ├── home.tsx
│   │   ├── contacts.tsx
│   │   └── settings.tsx
│   ├── emergency.tsx
│   ├── keyword-setup.tsx
│   └── _layout.tsx
├── components/
│   ├── AlertBanner.tsx
│   ├── ContactCard.tsx
│   ├── SensorStatus.tsx
│   └── EmergencyButton.tsx
├── services/
│   ├── api.ts               # axios instance with JWT interceptor
│   ├── alertService.ts      # trigger, verify, resolve alert
│   ├── pushService.ts       # register Expo push token
│   └── encryptionService.ts # AES-256 for local evidence files
├── hooks/
│   ├── useAuth.ts
│   ├── useLocation.ts
│   ├── useSensor.ts
│   └── useAlert.ts
├── store/
│   └── useStore.ts          # Zustand global state
├── tasks/
│   └── backgroundTask.ts    # expo-task-manager background sensor loop
├── constants/
│   └── config.ts            # API_BASE_URL, sensor thresholds
├── app.json                 # Expo config + permissions
├── eas.json                 # EAS Build profiles
└── .env.example
```

### app.json Permissions
```json
{
  "expo": {
    "plugins": [
      ["expo-location", {
        "locationAlwaysAndWhenInUsePermission": "RAKSHAK needs your location to alert contacts during emergencies."
      }],
      ["expo-notifications", {}],
      ["expo-av", {
        "microphonePermission": "RAKSHAK uses the microphone to detect your distress keyword."
      }],
      ["expo-camera", {
        "cameraPermission": "RAKSHAK records video evidence during emergencies."
      }],
      ["expo-contacts", {
        "contactsPermission": "RAKSHAK needs contacts to set up your trusted contacts list."
      }]
    ],
    "android": {
      "permissions": [
        "ACCESS_BACKGROUND_LOCATION",
        "FOREGROUND_SERVICE",
        "RECORD_AUDIO"
      ]
    }
  }
}
```

### Key Expo Libraries
| Feature | Library |
|---|---|
| Audio / microphone | `expo-av` |
| Background tasks | `expo-task-manager` + `expo-background-fetch` |
| GPS / location | `expo-location` |
| Camera | `expo-camera` |
| Contacts picker | `expo-contacts` |
| Push notifications | `expo-notifications` |
| Secure token storage | `expo-secure-store` |
| Gyro / Accelerometer | `expo-sensors` |
| Maps (OSM, free) | `react-native-maps` |
| Navigation | `expo-router` |
| HTTP client | `axios` |
| State management | `zustand` |
| Encryption | `crypto-js` |

### OpenStreetMap Setup (Free — No API Key)
```tsx
import MapView, { UrlTile } from 'react-native-maps';

<MapView style={{ flex: 1 }} initialRegion={region}>
  <UrlTile
    urlTemplate="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    maximumZ={19}
    flipY={false}
  />
</MapView>
```

### APIs to Consume (from Agent 2)
```
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/token/refresh/
GET    /api/profile/
PUT    /api/profile/update/
GET    /api/contacts/
POST   /api/contacts/add/
DELETE /api/contacts/<id>/remove/
POST   /api/keyword/upload/
POST   /api/alerts/trigger/
POST   /api/alerts/verify/
GET    /api/alerts/nearby/
POST   /api/alerts/<id>/resolve/
POST   /api/evidence/upload/
DELETE /api/evidence/<id>/
```

### .env.example (Mobile)
```
API_BASE_URL=http://192.168.x.x:8000
# During demo: API_BASE_URL=https://xxxx.ngrok.io
```

### Notes
- Use `expo-dev-client` to test background tasks — Expo Go does NOT support them.
- Background location on Android requires `FOREGROUND_SERVICE` permission +
  `expo-location`'s `startLocationUpdatesAsync` with a registered background task.
- Expo push tokens look like `ExponentPushToken[xxxxxx]` — send to backend on login.
- Target Android 10+ (API 29+) and iOS 14+.

---

## 👤 AGENT 2 — Backend API Agent (Django + MongoDB Atlas)

### Role
Build the Django REST Framework backend using **PyMongo** to connect to **MongoDB Atlas free M0 cluster**. Use Expo Push API (free HTTP endpoint) for notifications. No Firebase, no SQL, no paid services.

### Responsibilities
- Set up Django project with apps: `users`, `alerts`, `contacts`, `evidence`, `notifications`
- Connect to MongoDB Atlas using **PyMongo**
- Implement JWT auth using `djangorestframework-simplejwt`
- Build all REST API endpoints listed below
- Implement Haversine formula for nearby-user geospatial query (no PostGIS needed)
- Build Django Channels WebSocket consumer for live location streaming
- Send push notifications via **Expo Push HTTP API** (free, no Firebase SDK)
- Handle AES-256 encrypted file uploads — save to local `MEDIA_ROOT`
- Build alert lifecycle: `created → verified → active → resolved`
- Rate limiting via `django-ratelimit` (free)
- Log errors to file using Django's built-in logging

### MongoDB Connection (core/db.py)
```python
from pymongo import MongoClient
from decouple import config

client = MongoClient(config("MONGODB_URI"))
db = client["rakshak_db"]

users_col     = db["users"]
contacts_col  = db["trusted_contacts"]
keywords_col  = db["distress_keywords"]
alerts_col    = db["alerts"]
evidence_col  = db["evidence"]
logs_col      = db["alert_logs"]
```

### API Endpoints
```
AUTH:
  POST   /api/auth/register/
  POST   /api/auth/login/
  POST   /api/auth/token/refresh/

PROFILE:
  GET    /api/profile/
  PUT    /api/profile/update/

TRUSTED CONTACTS:
  GET    /api/contacts/
  POST   /api/contacts/add/
  DELETE /api/contacts/<id>/remove/

DISTRESS KEYWORD:
  POST   /api/keyword/upload/

ALERTS:
  POST   /api/alerts/trigger/
  POST   /api/alerts/verify/
  GET    /api/alerts/nearby/
  POST   /api/alerts/<id>/resolve/

EVIDENCE:
  POST   /api/evidence/upload/
  GET    /api/evidence/<alert_id>/
  DELETE /api/evidence/<id>/

WEBSOCKET:
  ws:// /ws/location/<alert_id>/
```

### Haversine Nearby Query (Free — No PostGIS)
```python
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_nearby_alerts(user_lat, user_lon, radius_m=1000):
    active = alerts_col.find({"status": "active"})
    nearby = []
    for alert in active:
        dist = haversine(user_lat, user_lon, alert["lat"], alert["lng"])
        if dist <= radius_m:
            nearby.append({
                "alert_id": str(alert["_id"]),
                "approximate_area": alert.get("area_name", "Nearby"),
                "timestamp": alert["created_at"],
                "threat_level": alert["threat_level"]
                # NEVER include: user_id, name, phone, exact GPS
            })
    return nearby
```

### Expo Push Notifications (Free — No Firebase)
```python
import requests

def send_expo_push(expo_token, title, body, data={}):
    requests.post(
        "https://exp.host/--/api/v2/push/send",
        json={
            "to": expo_token,
            "title": title,
            "body": body,
            "data": data,
            "sound": "default",
            "priority": "high"
        }
    )
```

### AES-256 Encryption (Free — `cryptography` lib)
```python
from cryptography.fernet import Fernet
from decouple import config

fernet = Fernet(config("AES_ENCRYPTION_KEY").encode())

def encrypt_file(file_bytes: bytes) -> bytes:
    return fernet.encrypt(file_bytes)

def decrypt_file(encrypted_bytes: bytes) -> bytes:
    return fernet.decrypt(encrypted_bytes)
```

### Key Files to Create
```
backend/
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py          # Django Channels ASGI
│   └── db.py            # PyMongo connection
├── users/
│   └── views.py
├── alerts/
│   ├── views.py
│   ├── haversine.py
│   └── consumers.py     # Channels WebSocket consumer
├── contacts/
│   └── views.py
├── evidence/
│   ├── views.py
│   └── encryption.py
├── notifications/
│   └── expo_push.py
├── media/               # MEDIA_ROOT — local file storage
│   ├── evidence/
│   └── keywords/
├── logs/
│   └── rakshak.log
├── manage.py
├── requirements.txt
└── .env.example
```

### requirements.txt
```
django>=4.2
djangorestframework
djangorestframework-simplejwt
pymongo[srv]
channels
channels-redis
cryptography
requests
python-decouple
django-cors-headers
django-ratelimit
```

### .env.example (Backend)
```
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/rakshak_db?retryWrites=true&w=majority

REDIS_URL=redis://localhost:6379

MEDIA_ROOT=./media
MEDIA_URL=/media/

AES_ENCRYPTION_KEY=your-32-byte-fernet-key-here

EXPO_PUSH_URL=https://exp.host/--/api/v2/push/send
```

### Notes
- Use `python-decouple` to load `.env` variables.
- Redis runs locally (`redis-server`) — free.
- Evidence files saved to `backend/media/evidence/` (local disk).
- Use `bson.ObjectId` for MongoDB `_id` fields.
- Never expose victim PII in community alert responses.

---

## 👤 AGENT 3 — AI/ML Agent (TensorFlow Lite)

### Role
Design, train, optimize, and export the on-device ML models for automatic threat detection. All tools are free and open source. Use Google Colab (free) if local GPU is unavailable.

### Responsibilities
- Build and train **Voice Keyword Detection Model**
  - Input: audio → MFCC features via `librosa`
  - Architecture: lightweight CNN
  - Works in noisy environments with audio augmentation
  - Export: `keyword_model/model.tflite` (INT8 quantized)
- Build and train **Motion Anomaly Detection Model**
  - Input: gyroscope + accelerometer time-series (2–3 second window, 50Hz)
  - Output: `normal` / `suspicious` / `high-risk`
  - Architecture: 1D-CNN or LSTM
  - Export: `motion_model/model.tflite` (INT8 quantized)
- Build **Threat Fusion Logic**
  - Combines voice score (0–1) + motion score (0–1) → `LOW / MEDIUM / HIGH`
  - Rule-based combiner (runs on device, no server call)
- Optimize: < 5MB per model, < 200ms inference on mid-range Android
- Write `integration_guide.md` for Agent 1 (Expo mobile)

### Deliverables
```
ml/
├── keyword_model/
│   ├── train.py
│   ├── augment.py
│   ├── dataset/
│   ├── model.tflite
│   └── README.md
├── motion_model/
│   ├── train.py
│   ├── dataset/
│   ├── model.tflite
│   └── README.md
├── fusion/
│   ├── fusion_logic.py
│   └── README.md
├── integration_guide.md
└── requirements.txt
```

### requirements.txt
```
tensorflow>=2.12
librosa
numpy
pandas
scikit-learn
matplotlib
```

### Notes
- Use Google Colab (free GPU) for training if local machine is slow.
- Use open-source datasets only (no paid datasets).
- Document accuracy, false positive rate, and inference latency in each `README.md`.
- Integration in Expo: use `react-native-fast-tflite`; place `.tflite` files in `mobile/assets/models/`.

---

## 👤 AGENT 4 — Database & Infrastructure Agent (Local + Free)

### Role
Set up MongoDB Atlas free cluster, local Redis, local file storage, Docker for local dev, and ngrok for demo tunneling. No paid cloud services.

### Responsibilities
- Set up **MongoDB Atlas M0 free cluster** and provide `MONGODB_URI`
- Create all required collections and indexes in Atlas
- Set up **local Redis** for Django Channels
- Create **Docker Compose** for local dev (Django + Redis)
- Set up `MEDIA_ROOT` folder structure for local file storage
- Configure **ngrok** for tunneling localhost during demo
- Define all `.env` variables for every agent
- Set up Django file logging
- Write full local setup `README.md`

### MongoDB Atlas Setup
```
1. https://cloud.mongodb.com → Create free account (no credit card)
2. Create FREE M0 cluster → choose nearest region
3. Database Access → Create user with readWrite on rakshak_db
4. Network Access → Add IP 0.0.0.0/0 (dev only)
5. Connect → Drivers → Python → Copy connection string
6. Add to .env as MONGODB_URI
```

### MongoDB Indexes (run in Atlas UI → Shell)
```javascript
use rakshak_db

db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "phone": 1 }, { unique: true })
db.users.createIndex({ "location": "2dsphere" })

db.alerts.createIndex({ "status": 1, "created_at": -1 })
db.alerts.createIndex({ "location": "2dsphere" })

db.trusted_contacts.createIndex({ "user_id": 1 })
db.evidence.createIndex({ "alert_id": 1 })
```

### Docker Compose (Local Dev Only)
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./backend:/app
      - ./backend/media:/app/media
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### ngrok Setup (Free Demo Tunneling)
```bash
# Download ngrok free tier from https://ngrok.com/download
ngrok http 8000
# Copy https://xxxx.ngrok.io → set as API_BASE_URL in mobile .env
```

### Local Media Structure
```
backend/media/
├── evidence/     # AES-256 encrypted audio/video files
└── keywords/     # User distress keyword voice samples
```

### .env.example (Shared)
```
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Atlas
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/rakshak_db?retryWrites=true&w=majority

# Redis (local)
REDIS_URL=redis://localhost:6379

# File Storage (local)
MEDIA_ROOT=./media
MEDIA_URL=/media/

# Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
AES_ENCRYPTION_KEY=

# Expo Push (no key needed — public endpoint)
EXPO_PUSH_URL=https://exp.host/--/api/v2/push/send
```

### Full Local Setup Instructions (README.md to write)
```bash
# 1. Clone repo
git clone https://github.com/your-org/rakshak.git && cd rakshak

# 2. Start Redis
redis-server

# 3. Backend setup
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Fill MONGODB_URI and AES_ENCRYPTION_KEY
python manage.py runserver

# 4. Tunnel for mobile device testing
ngrok http 8000
# Paste https URL into mobile/.env as API_BASE_URL

# 5. Mobile setup
cd ../mobile
npm install
npx expo start
# Scan QR with Expo Go OR run on dev-client build
```

---

## 👤 AGENT 5 — Security Agent

### Role
Audit and harden every layer of RAKSHAK. Ensure no PII leaks in community alerts, all evidence is encrypted, and endpoints are rate-limited. All tools are free.

### Responsibilities
- Audit all API endpoints for auth/authorization gaps
- Verify Fernet AES-256 encryption is applied to all evidence files before disk write
- Ensure community alerts are fully anonymous — strip all PII before broadcast
- Add rate limiting using `django-ratelimit` (free)
- Add input validation and sanitization on all inputs
- Verify JWT configuration (access: 15min, refresh: 7 days, rotation on)
- Implement user-controlled evidence deletion (`DELETE /api/evidence/<id>/`)
- Audit MongoDB Atlas user permissions (readWrite only, no admin role)
- Write `SECURITY.md`, `THREAT_MODEL.md`, `PRIVACY_POLICY.md`

### Key Areas to Secure
```
1. Auth         → JWT: access 15min, refresh 7 days, rotation enabled
                  Brute-force: max 5 login attempts per IP per minute
2. Evidence     → Fernet AES-256 encrypt before writing to MEDIA_ROOT
                  User can delete their own evidence only
3. Alerts       → Strip user_id, name, phone, exact GPS from community broadcast
4. Location     → WebSocket auto-closes on alert resolve or after 30min timeout
5. API          → Rate limiting via django-ratelimit on login + alert trigger
                  Input sanitization on all endpoints
6. Mobile       → JWT in expo-secure-store only (never AsyncStorage or console.log)
7. MongoDB      → Atlas DB user: readWrite on rakshak_db only, no admin
```

### Rate Limiting (Free — `django-ratelimit`)
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', block=True)    # login
@ratelimit(key='user', rate='10/m', block=True)  # alert trigger
```

### Deliverables
```
docs/
├── SECURITY.md        # All measures with code references
├── THREAT_MODEL.md    # Top 10 attack vectors + mitigations
└── PRIVACY_POLICY.md  # Data policy for app store submission
```

---

## 🔄 AGENT COORDINATION

### Integration Points
| Agent | Needs From |
|---|---|
| Agent 1 (Mobile) | Agent 2: API endpoint list + response schemas |
| Agent 1 (Mobile) | Agent 3: `.tflite` files + `integration_guide.md` |
| Agent 1 (Mobile) | Agent 4: `API_BASE_URL` (ngrok URL) |
| Agent 2 (Backend) | Agent 4: `MONGODB_URI`, `REDIS_URL`, `AES_ENCRYPTION_KEY` |
| Agent 3 (ML) | Agent 1: sensor data format (sampling rate, value units) |
| Agent 5 (Security) | Reviews all agents before final submission |

### Development Order
```
Phase 1: Agent 4 → Atlas cluster setup + Redis + Docker + .env
Phase 2: Agent 2 → Django backend + MongoDB + all APIs
Phase 3: Agent 3 → Train ML models + export .tflite
Phase 4: Agent 1 → Expo mobile app (APIs + models)
Phase 5: Agent 5 → Security audit + hardening
```

---

## ✅ DEFINITION OF DONE (Per Agent)

- [ ] All responsibilities implemented
- [ ] Unit tests written and passing
- [ ] Every function/class documented with comments
- [ ] `.env.example` updated with any new variables
- [ ] `README.md` exists with setup instructions
- [ ] Integration with other agents tested end-to-end
- [ ] Agent 5 (Security) has reviewed and signed off
- [ ] No paid services used (MongoDB Atlas M0 free tier is the only exception)

---

*RAKSHAK v1.0 — Hack-O-Holic 4.0 | Stack: Expo + Django + MongoDB Atlas Free + TFLite + Expo Push*
