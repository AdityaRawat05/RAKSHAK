import math
from core.db import alerts_col, users_col

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
        lat = alert.get("lat")
        lng = alert.get("lng")
        if lat is not None and lng is not None:
            dist = haversine(user_lat, user_lon, lat, lng)
            if dist <= radius_m:
                nearby.append({
                    "alert_id": str(alert["_id"]),
                    "timestamp": alert.get("created_at"),
                    "threat_level": alert.get("threat_level", "UNKNOWN")
                    # Deliberately omitting user_id, name, phone, exactly precise GPS
                })
                
    return nearby

def get_nearby_users(center_lat, center_lon, radius_m=200):
    """
    Finds all users with push tokens whose last known location is within
    the target radius.
    """
    # In a production environment with millions of users, this would use
    # MongoDB's built-in 2dsphere index and $near query.
    # For Rakshak's initial scale, we use a manual filter loop.
    users = users_col.find({"location": {"$ne": None}, "expo_push_token": {"$ne": None}})
    nearby_tokens = []
    
    for user in users:
        loc = user.get("location")
        u_lat = loc.get("lat")
        u_lng = loc.get("lng")
        
        if u_lat and u_lng:
            dist = haversine(center_lat, center_lon, u_lat, u_lng)
            if dist <= radius_m:
                nearby_tokens.append(user["expo_push_token"])
                
    return nearby_tokens
