# PROMPT.md — RAKSHAK: AI-Powered Proactive Women Safety System
> Copy the prompt for each agent and paste it into a new AI agent session.
> Always attach AGENT.md alongside each prompt so the agent has full project context.
> Run agents in order: Agent 4 → Agent 2 → Agent 3 → Agent 1 → Agent 5

---

## 🤖 AGENT 1 PROMPT — Expo Mobile App

```
You are an expert React Native + Expo developer. Your task is to build the
RAKSHAK mobile app — an AI-powered women safety system.

Read the AGENT.md file first. Follow ONLY the AGENT 1 section.

=== PROJECT CONTEXT ===
Project: RAKSHAK — AI-Powered Proactive Women Safety System
Framework: Expo SDK (managed workflow, TypeScript)
Database: MongoDB Atlas (backend handles this — you only call REST APIs)
Push Notifications: Expo Push Notification Service (FREE — no Firebase)
Maps: OpenStreetMap via react-native-maps (FREE — no Google API key)
No paid services allowed.

=== YOUR TASKS ===

STEP 1 — Project Setup:
Initialize the project:
  npx create-expo-app rakshak-mobile --template blank-typescript
Create this folder structure:
  app/ (auth)/ (tabs)/ emergency.tsx keyword-setup.tsx _layout.tsx
  components/ services/ hooks/ store/ tasks/ constants/

STEP 2 — Navigation:
Use Expo Router for file-based navigation.
Screens to build:
  - (auth)/login.tsx         → Login with phone/email + password
  - (auth)/register.tsx      → Register + upload Expo push token to backend
  - (tabs)/home.tsx          → Sensor status, active alert indicator, big SOS button
  - (tabs)/contacts.tsx      → Add/remove trusted contacts (expo-contacts picker)
  - (tabs)/settings.tsx      → Keyword setup, sensitivity, profile
  - emergency.tsx            → Full-screen emergency overlay with live map + cancel button
  - keyword-setup.tsx        → Record custom distress keyword using expo-av

STEP 3 — Sensor Background Task:
File: tasks/backgroundTask.ts
- Register a background task using expo-task-manager
- In the task, continuously read:
    expo-sensors: Accelerometer + Gyroscope (50Hz)
    expo-location: GPS coordinates
    expo-av: Microphone audio buffer
- Run the .tflite models (motion + keyword) on sensor data
- If threat detected → call POST /api/alerts/trigger/ via alertService.ts

STEP 4 — Push Notifications:
File: services/pushService.ts
- On app launch, call expo-notifications to get Expo push token
  (format: ExponentPushToken[xxxxxx])
- Send this token to backend: PUT /api/profile/update/ with { expo_push_token }
- Handle incoming push notifications (show alert banner)

STEP 5 — Maps (OpenStreetMap — Free):
In emergency.tsx, show live location map using react-native-maps with OSM tiles:
  <MapView style={{ flex: 1 }} initialRegion={region}>
    <UrlTile
      urlTemplate="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      maximumZ={19}
      flipY={false}
    />
  </MapView>
DO NOT use Google Maps provider — no API key, no billing.

STEP 6 — API Service:
File: services/api.ts
- Create axios instance with base URL from .env (API_BASE_URL)
- Add JWT interceptor: attach Authorization: Bearer <token> to every request
- Add refresh token logic on 401 responses
- Store/retrieve tokens using expo-secure-store (NEVER AsyncStorage)

STEP 7 — All API Integrations:
Connect to these backend endpoints:
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

STEP 8 — State Management:
Use Zustand. Store: auth token, user profile, active alert state, contacts list.

STEP 9 — app.json Permissions:
Declare all permissions for: expo-location (always), expo-av (mic),
expo-camera, expo-contacts, expo-notifications.
Android permissions: ACCESS_BACKGROUND_LOCATION, FOREGROUND_SERVICE, RECORD_AUDIO

STEP 10 — eas.json:
Create EAS build profiles: development, preview, production.

STEP 11 — .env.example:
  API_BASE_URL=http://192.168.x.x:8000

STEP 12 — README.md:
Write setup instructions:
  npm install → npx expo start → scan QR (Expo Go for basic testing)
  eas build --profile development --platform android (for background tasks + sensors)

=== RULES ===
- Never use AsyncStorage for sensitive data — use expo-secure-store only
- Never hardcode API URLs — use .env via expo-constants
- Never use Google Maps — use OpenStreetMap only (no API key needed)
- Never use Firebase directly — Expo push handles notifications
- Add TypeScript types everywhere
- Comment every function
- Write unit tests for all services and hooks
```

---

## 🤖 AGENT 2 PROMPT — Django Backend API

```
You are an expert Django + MongoDB backend developer. Your task is to build
the RAKSHAK REST API backend.

Read the AGENT.md file first. Follow ONLY the AGENT 2 section.

=== PROJECT CONTEXT ===
Project: RAKSHAK — AI-Powered Proactive Women Safety System
Backend: Django + Django REST Framework
Database: MongoDB Atlas (free M0 tier) via PyMongo (NO Django ORM, NO SQL)
Push Notifications: Expo Push HTTP API (free — https://exp.host/--/api/v2/push/send)
File Storage: Local MEDIA_ROOT (no AWS S3, no Firebase Storage)
Encryption: Fernet AES-256 via Python cryptography library
No paid services allowed.

=== YOUR TASKS ===

STEP 1 — Project Setup:
  django-admin startproject core .
  python manage.py startapp users
  python manage.py startapp alerts
  python manage.py startapp contacts
  python manage.py startapp evidence
  python manage.py startapp notifications

STEP 2 — MongoDB Connection:
File: core/db.py
Connect to MongoDB Atlas using PyMongo:
  from pymongo import MongoClient
  from decouple import config
  client = MongoClient(config("MONGODB_URI"))
  db = client["rakshak_db"]
  users_col    = db["users"]
  contacts_col = db["trusted_contacts"]
  keywords_col = db["distress_keywords"]
  alerts_col   = db["alerts"]
  evidence_col = db["evidence"]
  logs_col     = db["alert_logs"]
Do NOT use Django models or migrations — use PyMongo directly for all DB operations.

STEP 3 — JWT Authentication:
Use djangorestframework-simplejwt.
Settings: access token expiry = 15 minutes, refresh = 7 days, rotation enabled.
Endpoints:
  POST /api/auth/register/  → hash password (bcrypt), insert user into users_col,
                              return JWT tokens
  POST /api/auth/login/     → verify password, return JWT tokens
  POST /api/auth/token/refresh/

STEP 4 — All API Endpoints:
Build these endpoints (all require JWT except register/login):

  GET    /api/profile/               → fetch user doc from users_col by user_id in JWT
  PUT    /api/profile/update/        → update name, phone, location, expo_push_token

  GET    /api/contacts/              → list contacts for current user
  POST   /api/contacts/add/          → insert into trusted_contacts col
  DELETE /api/contacts/<id>/remove/  → delete by _id (verify ownership first)

  POST   /api/keyword/upload/        → save audio file to MEDIA_ROOT/keywords/
                                      encrypt with Fernet, save metadata to keywords_col

  POST   /api/alerts/trigger/        → create alert doc in alerts_col with status=created
                                      send silent check-in push to user via Expo Push API
  POST   /api/alerts/verify/         → update alert status to active if confirmed
                                      send push to trusted contacts (expo_push_token from users_col)
                                      broadcast anonymous alert to nearby users (Haversine)
  GET    /api/alerts/nearby/         → run Haversine query, return ANONYMOUS results only
                                      (NO user_id, name, phone, or exact GPS in response)
  POST   /api/alerts/<id>/resolve/   → update alert status to resolved
                                      stop WebSocket location stream

  POST   /api/evidence/upload/       → encrypt file bytes with Fernet before saving to disk
                                      save metadata to evidence_col
  GET    /api/evidence/<alert_id>/   → return evidence list for alert (auth required)
  DELETE /api/evidence/<id>/         → user can only delete their own evidence

  WebSocket: /ws/location/<alert_id>/ → Django Channels consumer
    - On connect: verify JWT in query param
    - Receive: {lat, lng} → broadcast to group (trusted contacts watching)
    - Auto-close after 30 minutes or when alert resolved

STEP 5 — Haversine Nearby Query:
File: alerts/haversine.py
Implement Haversine formula in pure Python (no PostGIS needed):
  def haversine(lat1, lon1, lat2, lon2) → distance in meters
  def get_nearby_alerts(user_lat, user_lon, radius_m=1000) → list of anonymous alert dicts

STEP 6 — Expo Push Notifications:
File: notifications/expo_push.py
Send push via Expo Push HTTP API (free):
  POST https://exp.host/--/api/v2/push/send
  Body: { "to": expo_token, "title": ..., "body": ..., "sound": "default", "priority": "high" }
No Firebase SDK, no FCM, no service accounts needed.

STEP 7 — AES-256 File Encryption:
File: evidence/encryption.py
Use Python cryptography Fernet:
  fernet = Fernet(config("AES_ENCRYPTION_KEY").encode())
  encrypt_file(bytes) → encrypted bytes
  decrypt_file(bytes) → original bytes
Encrypt ALL evidence and keyword files before writing to disk.

STEP 8 — Rate Limiting:
Use django-ratelimit:
  @ratelimit(key='ip', rate='5/m', block=True)   on login view
  @ratelimit(key='user', rate='10/m', block=True) on alert trigger view

STEP 9 — Django Channels (WebSocket):
File: alerts/consumers.py + core/asgi.py
Set up Django Channels with local Redis (redis://localhost:6379).
WebSocket path: /ws/location/<alert_id>/
Validate JWT on connect. Broadcast location updates to a channel group.
Auto-disconnect after 30 minutes.

STEP 10 — Django File Logging:
In settings.py, configure LOGGING to write WARNING+ to logs/rakshak.log.
No Sentry, no paid monitoring.

STEP 11 — MEDIA_ROOT Setup:
In settings.py:
  MEDIA_ROOT = BASE_DIR / 'media'
  MEDIA_URL = '/media/'
Create folders: media/evidence/ and media/keywords/

STEP 12 — requirements.txt:
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
  bcrypt

STEP 13 — .env.example:
  SECRET_KEY=
  DEBUG=True
  ALLOWED_HOSTS=localhost,127.0.0.1
  MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/rakshak_db?retryWrites=true&w=majority
  REDIS_URL=redis://localhost:6379
  MEDIA_ROOT=./media
  MEDIA_URL=/media/
  AES_ENCRYPTION_KEY=
  EXPO_PUSH_URL=https://exp.host/--/api/v2/push/send

STEP 14 — README.md:
  python -m venv venv && source venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env
  python manage.py runserver

=== RULES ===
- Never use Django ORM or migrations — use PyMongo for all DB operations
- Never expose victim PII (name, phone, exact GPS) in community alert responses
- Never store unencrypted evidence files on disk
- Use bson.ObjectId for all MongoDB _id operations
- JWT required on every endpoint except /api/auth/register/ and /api/auth/login/
- Comment every view, serializer, and utility function
- Write unit tests for all views and utility functions
```

---

## 🤖 AGENT 3 PROMPT — AI/ML Models (TensorFlow Lite)

```
You are an expert ML engineer specializing in on-device AI and TensorFlow Lite.
Your task is to build the ML models for RAKSHAK — an AI-powered women safety system.

Read the AGENT.md file first. Follow ONLY the AGENT 3 section.

=== PROJECT CONTEXT ===
Project: RAKSHAK — AI-Powered Proactive Women Safety System
All models must run on-device (no server inference).
Framework: TensorFlow 2.x → export to TensorFlow Lite (.tflite)
Target: Android mid-range devices, < 5MB per model, < 200ms inference
Training: Use Google Colab (free GPU) if local machine is slow.
No paid datasets or services.

=== YOUR TASKS ===

STEP 1 — Voice Keyword Detection Model:
Folder: ml/keyword_model/

Goal: Detect the user's custom distress keyword from microphone audio even in noisy environments.

File: train.py
- Load audio samples from dataset/ (WAV files, 16kHz)
- Extract MFCC features using librosa (40 MFCC coefficients, hop_length=512)
- Augment data: mix with background noise, pitch shift ±2 semitones, speed change 0.9x–1.1x
- Architecture: lightweight CNN
    Input: (40, time_steps, 1)
    Conv2D(32) → BatchNorm → ReLU
    Conv2D(64) → BatchNorm → ReLU → MaxPool
    GlobalAveragePooling
    Dense(64) → Dropout(0.3)
    Dense(2, softmax)  # keyword / not-keyword
- Train with binary cross-entropy, Adam optimizer
- Save as keyword_model/saved_model/

File: augment.py
- Functions: add_noise(audio), pitch_shift(audio), time_stretch(audio)

Export to TFLite:
  converter = tf.lite.TFLiteConverter.from_saved_model('saved_model/')
  converter.optimizations = [tf.lite.Optimize.DEFAULT]
  converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
  tflite_model = converter.convert()
  with open('model.tflite', 'wb') as f:
      f.write(tflite_model)

STEP 2 — Motion Anomaly Detection Model:
Folder: ml/motion_model/

Goal: Classify motion patterns as normal / suspicious / high-risk using accelerometer + gyroscope data.

File: train.py
- Input: sensor readings at 50Hz, 2-second sliding window = 100 timesteps × 6 features
  Features: [acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z]
- Labels: 0=normal, 1=suspicious, 2=high-risk
- Normalize values to [-1, 1]
- Architecture: 1D-CNN
    Input: (100, 6)
    Conv1D(64, kernel=3) → BatchNorm → ReLU
    Conv1D(128, kernel=3) → BatchNorm → ReLU → MaxPool1D
    GlobalAveragePooling1D
    Dense(64) → Dropout(0.3)
    Dense(3, softmax)
- Train with sparse categorical cross-entropy, Adam optimizer
- Export to motion_model/model.tflite with INT8 quantization

STEP 3 — Threat Fusion Logic:
Folder: ml/fusion/

File: fusion_logic.py
Combine voice + motion risk scores into a final threat level:

  def fuse_threat(voice_score: float, motion_score: float) -> str:
      """
      voice_score: 0.0–1.0 (probability that keyword was detected)
      motion_score: 0.0–1.0 (probability of high-risk motion)
      Returns: 'LOW' | 'MEDIUM' | 'HIGH'
      """
      combined = (voice_score * 0.6) + (motion_score * 0.4)
      if combined >= 0.75:
          return 'HIGH'
      elif combined >= 0.45:
          return 'MEDIUM'
      else:
          return 'LOW'

This runs entirely on-device. No server call needed for fusion.

STEP 4 — Integration Guide for Expo (integration_guide.md):
Write clear instructions for Agent 1 to integrate the models in Expo:

  Library: react-native-fast-tflite
  Installation: npm install react-native-fast-tflite

  Place model files:
    mobile/assets/models/keyword_model.tflite
    mobile/assets/models/motion_model.tflite

  Loading:
    import { loadTensorflowModel } from 'react-native-fast-tflite';
    const keywordModel = await loadTensorflowModel(require('../assets/models/keyword_model.tflite'));
    const motionModel  = await loadTensorflowModel(require('../assets/models/motion_model.tflite'));

  Keyword inference:
    - Record 2-second audio chunk via expo-av
    - Convert to Float32Array of MFCC features (40 coefficients)
    - Run: const output = await keywordModel.run([mfccArray])
    - voice_score = output[0][1]  // probability of keyword class

  Motion inference:
    - Collect 100 sensor readings (2s at 50Hz) from expo-sensors
    - Normalize each reading to [-1, 1]
    - Flatten to Float32Array of shape (100 * 6 = 600)
    - Run: const output = await motionModel.run([sensorArray])
    - motion_score = output[0][2]  // probability of high-risk class

  Fusion:
    - Apply fusion_logic thresholds on device
    - If result is HIGH → call POST /api/alerts/trigger/ immediately
    - If MEDIUM → show silent check-in UI

STEP 5 — Benchmarks (in each README.md):
Document:
  - Model size (KB)
  - Accuracy on test set
  - False positive rate
  - Average inference latency on Android mid-range device
  - Battery usage estimate

STEP 6 — requirements.txt:
  tensorflow>=2.12
  librosa
  numpy
  pandas
  scikit-learn
  matplotlib
  soundfile

=== RULES ===
- All models must run on-device — NO server inference calls during threat detection
- Use only open-source, free datasets (or self-recorded samples)
- Apply INT8 post-training quantization to every model
- Target: each model < 5MB, inference < 200ms
- Document accuracy, false positive rate, and latency in each README.md
- Run inference on a background thread — never block the UI thread
- Comment all training code clearly
```

---

## 🤖 AGENT 4 PROMPT — Database & Infrastructure

```
You are an expert DevOps and database engineer. Your task is to set up all
infrastructure for RAKSHAK — a women safety system.

Read the AGENT.md file first. Follow ONLY the AGENT 4 section.

=== PROJECT CONTEXT ===
Project: RAKSHAK — AI-Powered Proactive Women Safety System
Database: MongoDB Atlas FREE M0 cluster (512MB, no credit card needed)
Cache / WebSocket: Redis (local, free)
File Storage: Local MEDIA_ROOT (no AWS S3, no Firebase)
Tunneling: ngrok free tier (for demo + mobile testing)
No paid cloud services allowed.

=== YOUR TASKS ===

STEP 1 — MongoDB Atlas Free Cluster Setup:
Write a detailed ATLAS_SETUP.md guide:
  1. Go to https://cloud.mongodb.com → sign up (no credit card)
  2. Click "Build a Database" → select FREE M0 tier → choose nearest region
  3. Database Access → Add Database User:
       Username: rakshak_user
       Password: (generate strong password)
       Role: readWriteAnyDatabase on rakshak_db
  4. Network Access → Add IP Address → 0.0.0.0/0 (allow all for dev)
  5. Connect → Drivers → Python 3.12+ → copy connection string
  6. Replace <password> in connection string → paste into .env as MONGODB_URI

STEP 2 — MongoDB Collections & Indexes:
Write a script: infra/scripts/setup_indexes.py
  Connect using MONGODB_URI from .env and create these indexes:

  users collection:
    { "email": 1 } unique=True
    { "phone": 1 } unique=True
    { "location": "2dsphere" }
    { "expo_push_token": 1 }

  alerts collection:
    { "status": 1, "created_at": -1 }
    { "location": "2dsphere" }
    { "user_id": 1 }

  trusted_contacts collection:
    { "user_id": 1 }

  evidence collection:
    { "alert_id": 1 }
    { "user_id": 1 }

  alert_logs collection:
    { "alert_id": 1, "timestamp": -1 }

STEP 3 — Docker Compose (Local Dev Only):
File: docker-compose.yml
Services:
  backend:
    build: ./backend
    ports: 8000:8000
    env_file: .env
    volumes: ./backend:/app and ./backend/media:/app/media
    depends_on: redis
  redis:
    image: redis:7-alpine
    ports: 6379:6379

File: backend/Dockerfile:
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

STEP 4 — Local Media Folder Structure:
Create these folders inside backend/:
  media/
  ├── evidence/     # AES-256 encrypted audio/video files
  └── keywords/     # User distress keyword voice samples
Add media/ to .gitignore (never commit user files to git).

STEP 5 — ngrok Setup Guide:
Write NGROK_SETUP.md:
  1. Download ngrok free: https://ngrok.com/download
  2. Sign up for free account → get auth token
  3. Run: ngrok config add-authtoken <your-token>
  4. Start tunnel: ngrok http 8000
  5. Copy the https://xxxx.ngrok.io URL
  6. Paste into mobile/.env as: API_BASE_URL=https://xxxx.ngrok.io
  Note: free tier URL changes every restart — update mobile .env each time

STEP 6 — Environment Variables:
File: .env.example (at project root — shared template for all agents)

  # Django
  SECRET_KEY=generate-with-python-secrets-module
  DEBUG=True
  ALLOWED_HOSTS=localhost,127.0.0.1

  # MongoDB Atlas (FREE M0)
  MONGODB_URI=mongodb+srv://rakshak_user:<password>@cluster0.xxxxx.mongodb.net/rakshak_db?retryWrites=true&w=majority

  # Redis (local)
  REDIS_URL=redis://localhost:6379

  # File Storage (local)
  MEDIA_ROOT=./media
  MEDIA_URL=/media/

  # AES-256 Encryption Key (generate with Fernet)
  # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  AES_ENCRYPTION_KEY=

  # Expo Push (no key needed — free public endpoint)
  EXPO_PUSH_URL=https://exp.host/--/api/v2/push/send

File: mobile/.env.example
  API_BASE_URL=http://192.168.x.x:8000

STEP 7 — Django Logging Config:
Write this in backend/core/settings.py LOGGING section:
  Log WARNING and above to logs/rakshak.log
  Log format: timestamp | level | module | message
  Create logs/ directory with .gitkeep

STEP 8 — .gitignore:
Create project-level .gitignore:
  .env
  *.pyc
  __pycache__/
  venv/
  media/
  logs/
  node_modules/
  .expo/
  dist/
  *.tflite (add to ml/.gitignore, link to releases instead)

STEP 9 — Full Local Setup README.md:
Write infra/README.md with complete step-by-step:
  Prerequisites: Python 3.11+, Node.js 18+, Redis, ngrok, Expo CLI, EAS CLI

  Backend:
    cd backend
    python -m venv venv && source venv/bin/activate  (or venv\Scripts\activate on Windows)
    pip install -r requirements.txt
    cp ../.env.example .env
    # Fill in MONGODB_URI and AES_ENCRYPTION_KEY in .env
    python infra/scripts/setup_indexes.py  # creates MongoDB indexes
    mkdir -p media/evidence media/keywords logs
    python manage.py runserver

  Redis (required for WebSocket):
    redis-server   (Mac/Linux)
    or: docker run -p 6379:6379 redis:7-alpine  (any platform)

  ngrok (for mobile testing):
    ngrok http 8000
    # Copy HTTPS URL → paste into mobile/.env as API_BASE_URL

  Mobile:
    cd mobile
    npm install
    cp .env.example .env
    # Set API_BASE_URL to ngrok URL or local IP
    npx expo start
    # For background tasks: use expo-dev-client build
    eas build --profile development --platform android

STEP 10 — GitHub Actions CI (Free):
File: .github/workflows/test.yml
  Trigger: on pull_request to main
  Steps:
    - Install Python 3.11
    - pip install -r backend/requirements.txt
    - Set test MONGODB_URI to a test Atlas cluster or mock
    - Run: python manage.py test

=== RULES ===
- Never commit .env files or media/ folder to git
- MongoDB Atlas M0 free tier only — never upgrade to paid
- Redis must run locally (not a cloud Redis service)
- All file storage is local MEDIA_ROOT — no S3, no Firebase Storage
- ngrok free tier only — URLs will change on restart (document this)
- Generate AES_ENCRYPTION_KEY using Fernet — document the generation command
```

---

## 🤖 AGENT 5 PROMPT — Security Audit

```
You are an expert application security engineer. Your task is to audit and
harden RAKSHAK — an AI-powered women safety system.

Read the AGENT.md file first. Follow ONLY the AGENT 5 section.

=== PROJECT CONTEXT ===
Project: RAKSHAK — AI-Powered Proactive Women Safety System
Backend: Django + MongoDB Atlas (PyMongo)
Mobile: Expo React Native
File Storage: Local MEDIA_ROOT (AES-256 encrypted)
Push: Expo Push API (free)
No paid services. Security tools must also be free.

=== YOUR TASKS ===

STEP 1 — JWT Authentication Audit:
Review backend/users/views.py and core/settings.py.
Verify and enforce:
  - Access token expiry: 15 minutes (SIMPLE_JWT ACCESS_TOKEN_LIFETIME)
  - Refresh token expiry: 7 days (REFRESH_TOKEN_LIFETIME)
  - Rotate refresh tokens: ROTATE_REFRESH_TOKENS = True
  - Blacklist used refresh tokens: BLACKLIST_AFTER_ROTATION = True
    (install: djangorestframework-simplejwt[crypto])
  - Password hashing: must use bcrypt (install: bcrypt, set PASSWORD_HASHERS in settings.py)
  - Brute-force protection on POST /api/auth/login/:
    @ratelimit(key='ip', rate='5/m', block=True)

STEP 2 — Evidence Encryption Audit:
Review evidence/encryption.py and evidence/views.py.
Verify:
  - All evidence files encrypted with Fernet BEFORE writing to disk (not after)
  - Unencrypted bytes never written anywhere (no temp files)
  - AES_ENCRYPTION_KEY loaded from .env only (never hardcoded)
  - Users can only delete their OWN evidence (check user_id in JWT vs evidence doc)
  - evidence/ folder in .gitignore (never committed to git)
If any issue found → fix it directly in the code.

STEP 3 — Community Alert Anonymity Audit:
Review alerts/views.py GET /api/alerts/nearby/ response.
The response MUST NEVER contain:
  - user_id
  - name
  - phone
  - email
  - exact latitude / longitude
Allowed fields only: alert_id, approximate_area, timestamp, threat_level.
Write a unit test that asserts none of the forbidden fields appear in the response.

STEP 4 — Location Privacy Audit:
Review alerts/consumers.py (Django Channels WebSocket).
Verify:
  - WebSocket requires valid JWT in query param on connect (reject unauthenticated connections)
  - Location stream auto-disconnects when alert status = resolved
  - Location stream auto-disconnects after 30-minute timeout
  - Location data is ONLY sent to trusted contacts of the victim (correct channel group)
If issues found → fix the consumer code.

STEP 5 — Rate Limiting Audit:
Review all sensitive views. Verify django-ratelimit is applied:
  POST /api/auth/login/        → 5 requests/minute per IP
  POST /api/alerts/trigger/    → 10 requests/minute per user
  POST /api/evidence/upload/   → 20 requests/minute per user
  POST /api/keyword/upload/    → 5 requests/minute per user
Install django-ratelimit if not present. Add decorators where missing.

STEP 6 — Input Validation Audit:
Review all API views. Verify:
  - All user inputs validated before MongoDB insertion (type, length, format checks)
  - No raw user input inserted into MongoDB queries (prevents NoSQL injection)
  - File uploads: validate MIME type and file size before saving
    (evidence: audio/video only, max 50MB; keywords: audio only, max 5MB)
  - Phone numbers: validate E.164 format
  - Email: validate format
Add validation where missing.

STEP 7 — MongoDB Atlas Security Audit:
Write ATLAS_SECURITY.md with checklist:
  - Atlas DB user: readWrite on rakshak_db only (NOT clusterAdmin or atlasAdmin)
  - IP whitelist: 0.0.0.0/0 is OK for dev → restrict to server IP for production
  - Connection uses SSL/TLS (enabled by default in Atlas URI with srv)
  - MONGODB_URI stored in .env only — never in source code or git history
  - Database name: rakshak_db — separate from other projects

STEP 8 — Mobile App Security Audit:
Review mobile/services/api.ts and mobile/store/useStore.ts.
Verify:
  - JWT tokens stored in expo-secure-store ONLY (never AsyncStorage, never console.log)
  - No sensitive data in console.log statements in production builds
  - API base URL from .env (never hardcoded)
  - All API calls use HTTPS (http:// only allowed for local dev via ngrok)
Flag all issues with severity: CRITICAL / HIGH / MEDIUM / LOW.

STEP 9 — Produce Security Documents:
File: docs/SECURITY.md
  Document every security measure implemented with code file references.
  Format: measure → implementation → file location → test coverage

File: docs/THREAT_MODEL.md
  List top 10 attack vectors for RAKSHAK + mitigation for each:
  Examples: JWT token theft, fake alert flooding, evidence tampering,
  community alert deanonymization, MongoDB injection, replay attacks, etc.

File: docs/PRIVACY_POLICY.md
  User-friendly privacy policy covering:
  - What data is collected (location, audio, contacts)
  - How it is stored (encrypted, local + Atlas)
  - Who can access it (user + trusted contacts only)
  - How to delete data (DELETE /api/evidence/<id>/ + account deletion)
  - No data sold to third parties
  - Data retention policy

=== RULES ===
- Do not just document — implement fixes directly in the code
- Label every issue found with: CRITICAL / HIGH / MEDIUM / LOW
- All CRITICAL and HIGH severity issues must be fixed before Agent 5 is done
- Use only free security tools (django-ratelimit, bcrypt, cryptography library)
- Never introduce paid monitoring or security services
- Write a unit test for every security measure you implement or verify
```

---

## 💡 How to Use These Prompts

### Step-by-step
1. **Always attach `AGENT.md`** when starting each agent session.
2. **Run agents in this order:**
   ```
   Agent 4 (Infra) → Agent 2 (Backend) → Agent 3 (ML) → Agent 1 (Mobile) → Agent 5 (Security)
   ```
3. **Pass outputs between agents:**
   - After Agent 4: share `.env.example` and `MONGODB_URI` with Agent 2
   - After Agent 2: share API endpoint list with Agent 1
   - After Agent 3: share `.tflite` files and `integration_guide.md` with Agent 1
   - After Agent 1 + 2: share full codebase with Agent 5 for audit

### Free Services Summary
| Service | Provider | Cost |
|---|---|---|
| Database | MongoDB Atlas M0 | Free forever |
| Push Notifications | Expo Push API | Free |
| Maps | OpenStreetMap | Free |
| Build | EAS Build (30 builds/month) | Free |
| Dev Tunnel | ngrok free tier | Free |
| Redis | Local (`redis-server`) | Free |
| File Storage | Local disk (`MEDIA_ROOT`) | Free |
| ML Training | Google Colab | Free |

---

*RAKSHAK v1.0 — Hack-O-Holic 4.0 | TechX — Graphic Era Hill University*
