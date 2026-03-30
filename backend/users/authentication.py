from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from core.db import users_col
from bson.objectid import ObjectId

class PyMongoUser:
    def __init__(self, user_doc):
        self.user_doc = user_doc
        self.id = str(user_doc.get('_id'))
        
    @property
    def is_authenticated(self):
        return True

    @property
    def pk(self):
        return self.id

class PyMongoJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Token contained no recognizable user identification')
            
        try:
            user_doc = users_col.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                raise AuthenticationFailed('User not found', code='user_not_found')
            return PyMongoUser(user_doc)
        except Exception:
            raise AuthenticationFailed('Invalid user ID', code='invalid_user')
