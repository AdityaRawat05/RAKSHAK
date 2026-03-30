from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.db import alerts_col, users_col, contacts_col
from bson.objectid import ObjectId
from rest_framework.permissions import IsAuthenticated
from .haversine import get_nearby_alerts, get_nearby_users
from notifications.expo_push import send_expo_push
from notifications.email_service import send_emergency_email
from datetime import datetime
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
import logging

logger = logging.getLogger('django')

class AlertTriggerView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='10/m', block=True))
    def post(self, request):
        user_id = request.user.id
        data = request.data
        lat = data.get('lat')
        lng = data.get('lng')
        threat_level = data.get('threat_level', 'LOW') # 'LOW', 'MEDIUM', 'HIGH'
        
        user_doc = users_col.find_one({"_id": ObjectId(user_id)})
        
        alert_doc = {
            "user_id": user_id,
            "status": "created",
            "lat": lat,
            "lng": lng,
            "threat_level": threat_level,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = alerts_col.insert_one(alert_doc)
        alert_id = str(result.inserted_id)
        
        logger.warning(f"🔔 SOS Triggered: Alert {alert_id} for user {user_id}")
        
        # Send silent check-in to user itself to prevent false alarms
        if user_doc and user_doc.get("expo_push_token"):
            send_expo_push(
                user_doc["expo_push_token"],
                "Are you safe?",
                "We detected a potential issue. Open the app to confirm or cancel.",
                {"alert_id": alert_id}
            )
            
        return Response({"message": "Alert triggered", "alert_id": alert_id}, status=status.HTTP_201_CREATED)

class AlertVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        alert_id = request.data.get('alert_id')
        
        if not alert_id:
            return Response({"error": "alert_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        alert_doc = alerts_col.find_one({"_id": ObjectId(alert_id), "user_id": user_id})
        if not alert_doc:
            return Response({"error": "Alert not found"}, status=status.HTTP_404_NOT_FOUND)
            
        alerts_col.update_one({"_id": ObjectId(alert_id)}, {"$set": {"status": "active"}})
        logger.warning(f"🚨 ALERT VERIFIED: Alert {alert_id} is now ACTIVE")
        
        # User details for broadcast
        user_doc = users_col.find_one({"_id": ObjectId(user_id)})
        lat, lng = alert_doc.get("lat"), alert_doc.get("lng")
        map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

        if user_doc:
            logger.warning(f"📡 Dispatching notifications for {user_doc.get('name')}...")
            
            # 1. Automate Email to Trusted Guardian
            contacts = list(contacts_col.find({"user_id": {"$in": [user_id, ObjectId(user_id)]}}))
            logger.warning(f"Found {len(contacts)} contacts for user {user_id}")
            
            for c in contacts:
                if c.get("email"):
                    logger.warning(f"📧 Sending emergency email to {c['email']}")
                    sent = send_emergency_email(c["email"], user_doc.get("name", "A Rakshak User"), map_link)
                    if sent:
                        logger.warning(f"✅ Email successfully sent to {c['email']}")
                    else:
                        logger.warning(f"❌ Failed to send email to {c['email']}")
                else:
                    logger.warning(f"⚠️ Contact {c.get('name')} is missing an email address")
                
            # 2. Community Broadcast (Push to Users within 200m)
            if lat and lng:
                nearby_tokens = get_nearby_users(lat, lng, radius_m=200)
                logger.warning(f"Found {len(nearby_tokens)} nearby devices")
                for token in nearby_tokens:
                    if token != user_doc.get("expo_push_token"):
                        send_expo_push(
                            token,
                            "🚨 DISTRESS NEARBY",
                            "Someone within 200m needs immediate help!",
                            {"alert_id": alert_id, "type": "NEARBY_SOS", "lat": lat, "lng": lng}
                        )

            # 3. Direct App Push to Trusted Contacts (standard)
            contact_phones = [c["phone"] for c in contacts]
            contact_users = users_col.find({"phone": {"$in": contact_phones}})
            # Count the number of push tokens found
            push_count = 0
            for contact_user in contact_users:
                if contact_user.get("expo_push_token"):
                    push_count += 1
                    send_expo_push(
                        contact_user["expo_push_token"],
                        "🚨 EMERGENCY ALERT",
                        f"{user_doc.get('name')} is in danger!",
                        {"alert_id": alert_id, "type": "EMERGENCY"}
                    )
            logger.warning(f"📱 Sent {push_count} push notifications to trusted contacts")
        
        return Response({"message": "Alert verified and contacts notified"}, status=status.HTTP_200_OK)

class AlertNearbyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lat = float(request.GET.get('lat'))
            lng = float(request.GET.get('lng'))
            radius = float(request.GET.get('radius_m', 1500))
        except (TypeError, ValueError):
            return Response({"error": "Invalid lat, lng, or radius"}, status=status.HTTP_400_BAD_REQUEST)
            
        nearby = get_nearby_alerts(lat, lng, radius)
        return Response(nearby, status=status.HTTP_200_OK)

class AlertResolveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, alert_id):
        user_id = request.user.id
        
        result = alerts_col.update_one(
            {"_id": ObjectId(alert_id), "user_id": user_id},
            {"$set": {"status": "resolved", "resolved_at": datetime.utcnow().isoformat()}}
        )
        
        if result.modified_count == 0:
            return Response({"error": "Alert not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({"message": "Alert resolved successfully"}, status=status.HTTP_200_OK)
