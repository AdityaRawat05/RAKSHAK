# 📈 RAKSHAK: Scalability & Performance Roadmap

Project Rakshak is designed to scale with its user base, using modern cloud patterns and on-device compute.

---

## 🏛️ Infrastructure & Scalability

### 1. Flexible Data Store (MongoDB)
- We use **MongoDB** for alert logs, user profiles, and contact associations. 
- **Benefit**: Horizontal scaling through sharding and flexible schema for evolving data logs from various device models.

### 2. High-Performance Geo-Queries
Distributing alerts to nearby users requires efficient spatial queries.
- **Current Alpha**: Uses **Haversine formula** calculations in the backend for 200m radius broadcasts.
- **Beta Roadmap**: Transitioning to **PostGIS** with GIST indexing for sub-millisecond query performance on millions of location breadcrumbs.

### 3. Asynchronous Task Orchestration
- **Daphne/Channels**: Handling real-time push notifications and long-running alert verification cycles without blocking the main event loop.
- **Celery with Redis**: Offloading non-critical tasks like evidence cleanup and periodic report generation.

---

## 🚀 Future Performance Optimizations

### 1. Distributed ML Inference (The Grid)
- Exploring collaborative on-device inference where multiple nearby devices can contribute to verifying a high-threat incident through shared acoustic/motion features (privacy-preserved).

### 2. Edge Processing
- Moving notification dispatch logic closer to the edge using **Cloudflare Workers** or **Global CDNs** to reduce latency during critical SOS moments.

### 3. On-Device Quantization (INT-8)
- Further optimizing TFLite models with **INT-8 quantization** to ensure 5ms inference pulses on even the most hardware-limited smartphones.

---

## 🔒 Security at Scale

- **Ratelimiting**: Enforcing a `10/m` rate limit on `/alerts/trigger/` to prevent DDoS or bot-attacks on the emergency system.
- **Micro-Services Architecture**: Preparing to decouple `alerts`, `notifications`, and `identity` into independent services for independent scaling.

---

> [!TIP]
> **Check Out**: `backend/alerts/views.py` and the `@ratelimit` decorator for security implementations.
