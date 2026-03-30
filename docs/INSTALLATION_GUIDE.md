# 🚀 RAKSHAK: Comprehensive Installation Guide

This guide will walk you through setting up the complete **RAKSHAK** system on your local machine for development and testing. The project consists of a **Django Backend** and an **Expo (React Native) Mobile App**.

---

## 📋 Prerequisites

Before you begin, ensure your system has the following installed:
1. **Python 3.10+**: For configuring the Django backend and ML scripts.
2. **Node.js (v18+) & npm**: For running the React Native mobile application.
3. **MongoDB Atlas Account**: Required for the database (See [ATLAS_SETUP.md](ATLAS_SETUP.md)).
4. **Ngrok**: Required to expose your local backend to the mobile app (See [NGROK_SETUP.md](NGROK_SETUP.md)).
5. **Expo Go App**: Install this on your physical iOS or Android device from the App Store / Google Play Store to run the mobile client.

---

## 🛠️ Step 1: Backend Setup (Django)

The backend handles alert processing, spatial mapping, and user identity management.

### 1. Initialize the Environment
Open a terminal and navigate to the backend directory:
```bash
cd Rakshak/backend
```

Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy the root `.env.example` file and configure it:
1. Copy `../.env.example` to `../.env`.
2. Generate an **AES Encryption Key** by running:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
3. Paste that key into the `AES_ENCRYPTION_KEY` variable in `.env`.
4. Follow the instructions in [ATLAS_SETUP.md](ATLAS_SETUP.md) to set your `MONGODB_URI`.

### 4. Run the Server
Because we use MongoDB directly via PyMongo for alerts, there are no traditional Django migrations needed for the core logic, but we must start the server:
```bash
python manage.py runserver 0.0.0.0:8000
```
Your backend is now running at `http://127.0.0.1:8000`.

---

## 🌍 Step 2: Securing the Connection (Ngrok)

Mobile devices cannot easily communicate with `localhost`. We will use Ngrok to expose the backend.

1. Follow the instructions in [NGROK_SETUP.md](NGROK_SETUP.md) to start your tunnel:
   ```bash
   ngrok http 8000
   ```
2. Copy the resulting **HTTPS Forwarding URL** (e.g., `https://1234abcd.ngrok-free.app`). Leave this terminal window running.

---

## 📱 Step 3: Mobile Setup (Expo)

The mobile codebase connects to the backend and runs the on-device TFLite models.

### 1. Initialize the Mobile Environment
Open a new terminal and navigate to the mobile folder:
```bash
cd Rakshak/mobile
npm install
```

### 2. Environment Variables
1. Create a `.env` file inside the `mobile/` directory (you can copy `.env.example`).
2. Set your `EXPO_PUBLIC_API_URL` (Wait, in App.tsx it looks for `EXPO_PUBLIC_API_URL` but `.env.example` says `API_BASE_URL`. Ensure you set it like this):
   ```env
   EXPO_PUBLIC_API_URL=https://1234abcd.ngrok-free.app/api
   ```
   *(Replace with the actual Ngrok URL you got in Step 2, and ensure `/api` is appended).*

### 3. Launch the Application
Start the Expo bundler:
```bash
npx expo start
```
1. Open the **Expo Go** app on your physical smartphone.
2. Scan the QR code displayed in your terminal.
3. The RAKSHAK app will bundle and open on your device!

---

## 🧠 Step 4: Machine Learning Setup

RAKSHAK relies on **TensorFlow Lite** models for on-device Keyword and Motion recognition.

1. In `mobile/App.tsx`, the system expects models at:
   - `assets/models/keyword_model.tflite`
   - `assets/models/motion_model.tflite`
2. Ensure you have run the training scripts located in the `ml/` directory (or use the pre-trained `.tflite` files provided inside the UI code).
3. Need to re-train? Navigate to `ml/fusion/` and view the docs for training custom keyword models using standard TensorFlow audio libraries.

---

## 🛑 Troubleshooting

- **Crash on Startup (Mobile)**: Make sure the `.tflite` assets exist and are correctly linked in `metro.config.js`. If you are testing in purely simulated mode, ensure the `safeLoadModel` function in `mlUtils.ts` is handling missing files gracefully.
- **Backend Connection Timeout**: Verify that your Ngrok URL is correct in `mobile/.env`, and that the Django server is still running. Also, check that your device and PC are on the same Wi-Fi network if not using Ngrok.
- **500 Server Error on SOS**: Verify your MongoDB URI is correct and network access in Atlas is set to `0.0.0.0/0`.

---

You're all set! RAKSHAK is now fully configured for development and debugging. Start simulating emergency responses securely!
