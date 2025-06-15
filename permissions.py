from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from django.conf import settings
import jwt
from accounts.models import CustomUser

class IsJWTAuthenticated(BasePermission):
    def has_permission(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise exceptions.AuthenticationFailed({"status_code": 401, "error": "Authorization header missing."})

        if not auth_header.startswith('Bearer '):
            raise exceptions.AuthenticationFailed({"status_code": 401, "error": "Invalid token format."})

        token = auth_header.split(' ')[1]
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded.get("user_id")
            return user_id
            

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed({"status_code": 401, "error": "Token has expired."})
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed({"status_code": 401, "error": "Invalid token."})
