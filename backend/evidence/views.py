import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.db import evidence_col, keywords_col
from bson.objectid import ObjectId
from rest_framework.permissions import IsAuthenticated
from .encryption import EncryptionService
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
import uuid

class KeywordUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='5/m', block=True))
    def post(self, request):
        user_id = request.user.id
        audio_file = request.FILES.get('file')

        if not audio_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file_extension = audio_file.name.split('.')[-1]
        allowed_extensions = ['wav', 'mp3', 'm4a']
        if file_extension.lower() not in allowed_extensions:
            return Response({"error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Encrypt the raw bytes
        raw_bytes = audio_file.read()
        encrypted_bytes = EncryptionService.encrypt_file(raw_bytes)

        # Save to disk
        filename = f"{user_id}_{uuid.uuid4().hex}.enc"
        file_path = os.path.join(settings.MEDIA_ROOT, 'keywords', filename)
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(encrypted_bytes)

        # Update metadata in DB
        doc = {
            "user_id": user_id,
            "file_path": file_path,
            "filename": filename,
            "encrypted": True
        }
        
        # Delete old keyword if any
        keywords_col.delete_many({"user_id": user_id})
        keywords_col.insert_one(doc)

        return Response({"message": "Distress keyword uploaded securely"}, status=status.HTTP_201_CREATED)

class EvidenceUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='20/m', block=True))
    def post(self, request):
        user_id = request.user.id
        alert_id = request.data.get('alert_id')
        evidence_file = request.FILES.get('file')

        if not alert_id or not evidence_file:
            return Response({"error": "alert_id and file are required"}, status=status.HTTP_400_BAD_REQUEST)

        raw_bytes = evidence_file.read()
        encrypted_bytes = EncryptionService.encrypt_file(raw_bytes)

        filename = f"{alert_id}_{uuid.uuid4().hex}.enc"
        file_path = os.path.join(settings.MEDIA_ROOT, 'evidence', filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(encrypted_bytes)

        doc = {
            "user_id": user_id,
            "alert_id": alert_id,
            "file_path": file_path,
            "filename": filename,
            "encrypted": True
        }
        
        result = evidence_col.insert_one(doc)
        
        return Response({
            "message": "Evidence uploaded securely",
            "evidence_id": str(result.inserted_id)
        }, status=status.HTTP_201_CREATED)

class EvidenceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, alert_id):
        user_id = request.user.id
        
        # Make sure user owns this alert or auth?
        # Note: If they are contacts they'd see it too, but omitting complex RBAC here for scope limits.
        # Only allowing creator to view their own for now based on prompt.
        
        docs = list(evidence_col.find({"alert_id": alert_id, "user_id": user_id}))
        for d in docs:
            d["_id"] = str(d["_id"])
            
        return Response(docs, status=status.HTTP_200_OK)

class EvidenceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, evidence_id):
        user_id = request.user.id
        
        try:
            doc = evidence_col.find_one({"_id": ObjectId(evidence_id), "user_id": user_id})
            if not doc:
                return Response({"error": "Evidence not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
                
            # Erase file
            if os.path.exists(doc['file_path']):
                os.remove(doc['file_path'])
                
            evidence_col.delete_one({"_id": ObjectId(evidence_id)})
            
            return Response({"message": "Evidence deleted forever"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid evidence ID"}, status=status.HTTP_400_BAD_REQUEST)
