# RAKSHAK Security Audit

This document outlines the security measures implemented across the ecosystem to ensure the safety of user data and resilience against attacks.

## 1. Authentication & Session Management
- **Measure**: JSON Web Token (JWT) architecture.
- **Implementation**: Used `rest_framework_simplejwt`. Access tokens expire in 15 minutes, refresh tokens exist for 7 days with rotation and blacklisting active.
- **File**: `backend/core/settings.py` -> `SIMPLE_JWT` configuration block.

## 2. Evidence Encryption
- **Measure**: 256-bit AES Fernet symmetric encryption.
- **Implementation**: Audio and Video bytes are encrypted fully *before* they are written to the local disk in `MEDIA_ROOT/evidence`. At no point is a cleartext evidence file at rest.
- **File**: `backend/evidence/encryption.py`

## 3. Rate Limiting protection
- **Measure**: Defending against Brute Force and API flooding.
- **Implementation**: Used `django-ratelimit`. Login is limited (5 requests/min per IP), and alert triggering is monitored (10 requests/min per User).
- **File**: `backend/users/views.py`

## 4. Community Alert Anonymization
- **Measure**: Zero Personally Identifiable Information (PII) is included in community-wide broadcasts (Haversine queries).
- **Implementation**: The nearby alerts endpoint strips `user_id`, `name`, `phone`, and explicit GPS metadata, replying only with imprecise zones and severity level.
- **File**: `backend/alerts/haversine.py` -> `get_nearby_alerts()`

## 5. WebSockets Stream Defense
- **Measure**: JWT required for live-stream location broadcasts.
- **Implementation**: Custom token validation parsing inside Django Channels before accepting connections in `LocationConsumer`. Additionally, socket automatically times out at 30 minutes.
- **File**: `backend/alerts/consumers.py`

## 6. Infrastructure Protection
- **Measure**: Pure PyMongo setup prevents historic SQL injection footprints. No unhardended ORM querying.
- **Implementation**: Uses MongoDB native queries to `users_col`, `alerts_col` etc. All MongoDB network traffic uses `mongodb+srv` TLS encapsulation out of the box.
