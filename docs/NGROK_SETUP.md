# Ngrok Setup Guide

RAKSHAK's mobile app (running in an emulator or on your physical device) needs to communicate with your Django backend, which is running locally on your computer at `http://127.0.0.1:8000`.

To make this possible, you will use **Ngrok** to create a secure tunnel and a public URL to your local server.

## Step 1: Setup Ngrok
1. Create a free account at [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup).
2. Download the Ngrok executable for your operating system.
3. Extract `ngrok.exe` and place it somewhere accessible.

## Step 2: Authenticate your machine
In your terminal, authenticate with your unique token (found on the Ngrok dashboard):
```bash
ngrok config add-authtoken <your-auth-token-here>
```

## Step 3: Run the Tunnel
While your Django server is running on port 8000, open a separate terminal and run:
```bash
ngrok http 8000
```

## Step 4: Update the Mobile App Configuration
Ngrok will display a forwarding URL, such as:
`Forwarding                    https://1234abcd.ngrok-free.app -> http://localhost:8000`

Copy the **HTTPS URL** and paste it into your `mobile/.env` file as your `API_BASE_URL`:
```
API_BASE_URL=https://1234abcd.ngrok-free.app
```

> [!WARNING]
> Because you are using the free tier of Ngrok, this URL will change every time you restart the Ngrok process. Remember to update the mobile app's `.env` file and restart the Expo app whenever the URL changes.
