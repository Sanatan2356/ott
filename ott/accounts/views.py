from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserToken, CustomUser
import random
import bcrypt
from datetime import datetime, timedelta
from django.utils.timezone import now
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from .serializers import (SignUpSerializer, MobileSerializer,VerifyPasscodeSerializer, 
                          OTPVerifySerializer, SetPasscodeSerializer, UserProfileSerializer, ChangePasswordSerializer)
from django.conf import settings
import jwt

class AdminSignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.create_admin(serializer.validated_data)
            return Response({"status_code": 201, "message": "Admin user created successfully."}, status=status.HTTP_201_CREATED)
        return Response({"status_code": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class SignUpView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({"status_code": 401, "message": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)

        if not auth_header.startswith('Bearer '):
            return Response({"status_code": 401, "message": "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = CustomUser.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({"status_code": 401, "message": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"status_code": 401, "message": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = SignUpSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status_code": 200, "message": "User profile created successfully."}, status=status.HTTP_200_OK)
        return Response({"status_code": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class MobileVerifyView(APIView):
    def post(self, request):
        serializer = MobileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status_code": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        
        otp = str(random.randint(100000, 999999))
        otp_expires = now() + timedelta(minutes=5)
        if not user:
            user = CustomUser.objects.create(phone_number=phone_number, otp=otp, otp_expires=otp_expires)
            user.set_unusable_password()
            user.save()
        else:
            user.otp = otp
            user.otp_expires = otp_expires
            user.save()

        return Response({"status_code": 200, "message": "OTP sent successfully", "otp": otp}, status=status.HTTP_200_OK)

class VerifyPasscodeView(APIView):
    def post(self, request):
        serializer = VerifyPasscodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status_code": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        login_type = serializer.validated_data['login_type']

        if login_type == 'passcode':
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            try:
                UserToken.objects.create(user=user, access_token=access_token, refresh_token=str(refresh))
            except Exception as e:
                return Response({"status_code": 500, "message": f"Error storing tokens: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"status_code": 200, "message": f"{login_type} verified successfully.", "access": access_token, "refresh": str(refresh)}, status=status.HTTP_200_OK)

class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            try:
                UserToken.objects.create(user=user, access_token=access_token, refresh_token=str(refresh))
            except Exception as e:
                return Response({"status_code": 500, "message": f"Error storing tokens: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"status_code": 200, "message": "OTP verified successfully.", "access": access_token, "refresh": str(refresh), "new_user": user.new_user}, status=status.HTTP_200_OK)

        return Response({"status_code": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class SetPasscodeView(APIView):
    def post(self, request):
        serializer = SetPasscodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status_code": 200, "message": "Passcode set successfully."}, status=status.HTTP_200_OK)
        return Response({"status_code": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({"status_code": 401, "message": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)
        if not auth_header.startswith('Bearer '):
            return Response({"status_code": 401, "message": "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            CustomUser.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({"status_code": 401, "message": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"status_code": 401, "message": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"status_code": 200, "message": "Logged out successfully."}, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({"status_code": 401, "message": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)
        if not auth_header.startswith('Bearer '):
            return Response({"status_code": 401, "message": "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = CustomUser.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({"status_code": 401, "message": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"status_code": 401, "message": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserProfileSerializer(user)
        return Response({"status_code": 200, "data": serializer.data}, status=status.HTTP_200_OK)

class AdminAllUsersView(ListAPIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({"status_code": 401, "message": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)
        if not auth_header.startswith('Bearer '):
            return Response({"status_code": 401, "message": "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = CustomUser.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({"status_code": 401, "message": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"status_code": 401, "message": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
        if user.is_superuser:
            users = CustomUser.objects.all()
            serializer = UserProfileSerializer(users, many=True)
            return Response({"status_code": 200, "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status_code": 403, "message": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

class ChangePasscodeView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_passcode = serializer.validated_data['new_passcode']
            hashed = bcrypt.hashpw(new_passcode.encode(), bcrypt.gensalt())
            user.passcode = hashed.decode()
            user.save()
            return Response({"status_code": 200, "message": "Passcode changed successfully."}, status=status.HTTP_200_OK)
        return Response({"status_code": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
