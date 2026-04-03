from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
import bcrypt
from core.db import users_col
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import RakshakProfile
import logging
from datetime import datetime
from bson.objectid import ObjectId

logger = logging.getLogger('django')

class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        data = request.data
        email = data.get('email', '').strip().lower()
        phone = data.get('phone')
        password = data.get('password')
        name = data.get('name')

        if not all([email, phone, password, name]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Check existing
        if users_col.find_one({"$or": [{"email": email}, {"phone": phone}]}):
            return Response({"error": "User with this email or phone already exists"}, status=status.HTTP_400_BAD_REQUEST)

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_doc = {
            "email": email,
            "phone": phone,
            "password": hashed,
            "name": name,
            "biometric_vector": data.get('biometric_vector'), # 128-dim Faceprint
            "expo_push_token": None,
            "location": None
        }

        
        result = users_col.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # --- NEW SHADOW USER & PROFILE INTEGRATION ---
        # Create a Django User and ensure RakshakProfile exists
        try:
            django_user, created = User.objects.get_or_create(username=email, email=email)
            if created:
                django_user.set_password(password)
                django_user.save()
            
            # --- DEFENSIVE: Ensure profile exists even if user was previously created ---
            from .signals import generate_rakshak_id
            profile, p_created = RakshakProfile.objects.get_or_create(user=django_user)
            if p_created or not profile.rakshak_id:
                profile.rakshak_id = generate_rakshak_id()
                profile.save()
                
            rakshak_id = profile.rakshak_id
            users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"rakshak_id": rakshak_id}})
        except Exception as e:
            logger.error(f"❌ Shadow User/Profile Sync Error: {e}")
            return Response({"error": "Identity synchronization failed. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        refresh = RefreshToken.for_user(django_user)
        refresh['user_id'] = user_id
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user_id,
            "rakshak_id": rakshak_id,
            "biometric_vector": user_doc.get("biometric_vector")
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
    def post(self, request):
        data = request.data
        email = data.get('email', '').strip().lower()
        password = data.get('password')

        if not email or not password:
            return Response({"error": "Missing email or password"}, status=status.HTTP_400_BAD_REQUEST)

        user_doc = users_col.find_one({"email": email})
        if not user_doc:
            logger.warning(f"❌ Login Failure: User not found with email '{email}'")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not bcrypt.checkpw(password.encode('utf-8'), user_doc['password'].encode('utf-8')):
            logger.warning(f"❌ Login Failure: Password mismatch for user '{email}'")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
        # --- SYSTEM SELF-HEALING: Ensure Django User exists for JWT ---
        django_user, created = User.objects.get_or_create(email=email, defaults={'username': email})
        if not created:
            django_user.set_password(password)
            django_user.save()
            
        # Ensure RakshakProfile exists for handshakes
        rakshak_profile, _ = RakshakProfile.objects.get_or_create(user=django_user)
        rakshak_id = rakshak_profile.rakshak_id
        user_id = str(user_doc["_id"])
        
        refresh = RefreshToken.for_user(django_user)
        # --- FIX: Manually inject MongoDB ID into token claims for PyMongoJWTAuthentication ---
        refresh['user_id'] = user_id

        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user_id,
            "rakshak_id": rakshak_id,
            "biometric_enrolled": bool(user_doc.get("biometric_vector")),
            "biometric_vector": user_doc.get("biometric_vector")
        }, status=status.HTTP_200_OK)



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_email = request.user.email.strip().lower()
        user_doc = users_col.find_one({"email": user_email}, {"password": 0})
        if not user_doc:
            return Response({"error": "User not found in custom database"}, status=status.HTTP_404_NOT_FOUND)
            
        user_doc["_id"] = str(user_doc["_id"])
        return Response(user_doc, status=status.HTTP_200_OK)
        
    def put(self, request):
        user_email = request.user.email.strip().lower()
        data = request.data
        update_fields = {}
        
        if 'name' in data: update_fields['name'] = data['name']
        if 'phone' in data: update_fields['phone'] = data['phone']
        if 'expo_push_token' in data: update_fields['expo_push_token'] = data['expo_push_token']
        if 'location' in data: update_fields['location'] = data['location']
        if 'biometric_vector' in data: update_fields['biometric_vector'] = data['biometric_vector']
        
        if not update_fields:
            return Response({"error": "No update fields provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        result = users_col.update_one({"email": user_email}, {"$set": update_fields})
        if result.matched_count == 0:
            return Response({"error": "Failed to locate user identity record"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)


class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        lat = request.data.get('lat')
        lng = request.data.get('lng')

        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Update MongoDB users collection with the new location as GeoJSON
        users_col.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"location": {"type": "Point", "coordinates": [float(lng), float(lat)]}, "last_seen": datetime.utcnow().isoformat()}}
        )

        return Response({"message": "Location synchronized"}, status=status.HTTP_200_OK)
