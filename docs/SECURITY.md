# 🛡️ RAKSHAK: Deep Security Architecture

This document delves into the specific cryptographic protocols, network resilience strategies, and system hardening configurations implemented in Project Rakshak.

---

## 1. Zero-Knowledge Cryptography (Symmetric AES-256)

### Data-at-Rest Protection Model
Audio signatures and continuous location breadcrumbs captured during a live emergency are highly sensitive. 
- **The Algorithm**: We use `FERNET`, an implementation of 128-bit or 256-bit symmetric AES (Advanced Encryption Standard) in CBC mode, paired with PKCS7 padding.
- **The Process**: Media generated is swept into memory, an Initial Vector (IV) is uniquely generated, and the payload is encrypted using the shared secret (`AES_ENCRYPTION_KEY` located in `.env`). 
- **The Outcome**: What is physically written to `MEDIA_ROOT/evidence/` or pushed to the S3 bucket is pure ciphertext (`.enc` format). If an attacker breaches the backend and downloads the entire `MEDIA_ROOT`, they cannot play an audio file or extract coordinates without the memory-resident environment key.

---

## 2. API Hardening and the Stateless JWT Approach

### The JSON Web Token Identity Model
Rakshak assumes a stateless approach to scale rapidly during mass broadcasts.
- **Access Tokens**: Short-lived signatures (15 minutes). If intercepted via MITM (Man In The Middle), the attack window expires almost instantly. Uses `HS256` hashing on the server-side `SECRET_KEY`.
- **Refresh Tokens**: Longer living (7 days), strictly rotated upon usage. If a user logs out, the specific token family is dynamically added to a denylist cache in Redis, invalidating any hijacked session.

### Rate-Limiting the Triggers (Leaky Bucket Strategy)
To prevent "DDoS" or spam flooding on the core emergency systems:
- **Authentication Routes (`/auth/login`)**: Strictly throttled down to **5 requests per minute** per IP address to block credential stuffing scripts.
- **Distress Triggers (`/alerts/trigger`)**: Throttle limits enforce a strict **10 per minute per User-ID**. If a mobile client loops out of control, the `django-ratelimit` interceptor drops the packet with HTTP 429 before touching the DB.

---

## 3. Communication Channel Armor

### WebSockets (Django Channels) Handshake
The live-tracking map establishes an asynchronous, bidirectional WebSocket connection.
- **Token Verification on Connect**: Standard WS protocols often struggle with headers. Rakshak's `LocationConsumer` parses the query string for `?token=JWT` during the physical handshake event. If it fails `jwt.decode` validation against the Django `User` model, the socket is dropped natively at the Daphne ASGI layer.
- **Time-To-Live (TTL)**: For defense-in-depth against zombie connections or dropped mobile signals, WebSocket connections forcefully close after **30 minutes of transmission**.

### TLS 1.3 Transport (Data-In-Transit)
All traffic is routed natively through HTTPS via load balancers. End-to-end symmetric encryption handles the rest. By mandating TLS 1.3, we ensure Forward Secrecy, eliminating risks from later key compromises.

---

## 4. Database Injection Immunity

Because Rakshak does not use traditional relational mapping (SQL) for high-velocity logs:
- **No SQL injection vectors**: We use pure `PyMongo`. We rely wholly on BSON (Binary JSON) object serialization.
- **Sanitization**: Standardized Pydantic-like Python serializers sanitize strings, integers, and floats before mapping them to the driver, rendering standard injection queries useless.
