from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
import bcrypt
from core.db import users_col
from bson.objectid import ObjectId
from rest_framework.permissions import IsAuthenticated
import logging

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
            "expo_push_token": None,
            "location": None
        }
        
        result = users_col.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Manual token generation to avoid SimpleJWT model requirements
        refresh = RefreshToken()
        refresh['user_id'] = user_id
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user_id
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
            
        user_id = str(user_doc["_id"])
        
        # Manual token generation to avoid SimpleJWT model requirements
        refresh = RefreshToken()
        refresh['user_id'] = user_id
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user_id
        }, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        user_doc = users_col.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if not user_doc:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        user_doc["_id"] = str(user_doc["_id"])
        return Response(user_doc, status=status.HTTP_200_OK)
        
    def put(self, request):
        user_id = request.user.id
        data = request.data
        update_fields = {}
        
        if 'name' in data: update_fields['name'] = data['name']
        if 'phone' in data: update_fields['phone'] = data['phone']
        if 'expo_push_token' in data: update_fields['expo_push_token'] = data['expo_push_token']
        if 'location' in data: update_fields['location'] = data['location']
        
        if not update_fields:
            return Response({"error": "No update fields provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        users_col.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
