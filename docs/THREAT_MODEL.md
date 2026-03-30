# Threat Model - RAKSHAK

### 1. Brute Force Login
- **Vector**: Repeated attempts to guess user passwords.
- **Mitigation**: Applied `django-ratelimit` intercepting IP flows peaking >5 times per minute. Passwords use BCrypt variable-cost hashing.

### 2. Physical Threat / Phone Theft
- **Vector**: Attacker takes victim's phone and turns off alerts or deletes evidence.
- **Mitigation**: Once triggered, WebSockets continue broadcasting un-interruptably. Local evidence files on the device are AES-256 encrypted natively preventing file-explorer snooping. Deletions require the JWT token to make `DELETE` HTTP requests which are validated against the server.

### 3. Community Alert PII Deanonymization
- **Vector**: Bad actor queries `/api/alerts/nearby/` continuously to map out victim locations.
- **Mitigation**: The endpoint is hard-coded to drop User identifier metadata, stripping `latitude/longitude` exact pairs in favor of area labels (e.g., threat radius zones).

### 4. Database Data Leakage
- **Vector**: A compromised backend server yields access to `MEDIA_ROOT`.
- **Mitigation**: All local files are stored as `.enc` ciphertext mapped through asymmetric / symmetric keys. Without `AES_ENCRYPTION_KEY` located only dynamically in memory through `.env`, all evidence is digitally inaccessible.

### 5. Fake Alert Flooding
- **Vector**: Rogue accounts spam the community system.
- **Mitigation**: `AlertTriggerView` is strictly rate-limited mapped to the authenticated user token (10 limits per minute). False reporting profiles can be purged via MongoDB directly.

### 6. Location WebSocket Hijacking
- **Vector**: Listeners mapping to Socket URLs intercepting latitude traces.
- **Mitigation**: Django Channels consumer fetches JWT `?token=` and rejects any handshake not mapped to either the victim themselves or authorized responders. Auto-timeout enforced after 30 minutes cuts off zombie subscriptions.
