from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserToken,CustomUser
import random
from datetime import datetime, timedelta
from django.utils.timezone import now  # Use timezone-aware datetime
from rest_framework.exceptions import NotFound

from .serializers import (SignUpSerializer,LoginSerializer,OTPVerifySerializer
                            ,SetPasscodeSerializer)
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_otp(phone_number):
    user = CustomUser.objects.filter(phone_number=phone_number).first()
    if not user:
        raise NotFound("User with this phone number does not exist.")

    otp = str(random.randint(100000, 999999))
    otp_expires = now() + timedelta(minutes=5)

    user.otp = otp
    user.otp_expires = otp_expires
    user.save()

  
    return {"message": "OTP generated and sent.", "otp": otp}  # Don't return OTP in production

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login_type = serializer.validated_data['login_type']
        print(login_type)
        if login_type == 'otp':
            # Trigger OTP sending logic
            result=generate_otp(user.phone_number)
            return Response(result, status=200)

            # return Response({"message": "OTP sent to phone number."})
        if login_type=='passcode':

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            try:
                # Store tokens in UserToken table
                UserToken.objects.create(
                    user=user,
                    access_token=access_token,
                    refresh_token=str(refresh)
                )
            except Exception as e:
                return Response({
                    "message": "Error storing tokens",
                    "error": str(e),
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "message": "OTP verified successfully.",
                "access": access_token,
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)



class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            try:
                # Store tokens in UserToken table
                UserToken.objects.create(
                    user=user,
                    access_token=access_token,
                    refresh_token=str(refresh)
                )
            except Exception as e:
                return Response({
                    "message": "Error storing tokens",
                    "error": str(e),
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "message": "OTP verified successfully.",
                "access": access_token,
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   

class SetPasscodeView(APIView):
    def post(self, request):
        serializer = SetPasscodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Passcode set successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
import jwt

class LogoutView(APIView):

    def post(self, request):
        # Extract the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({"error": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)

        if not auth_header.startswith('Bearer '):
            return Response({"error": "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        try:
            # Decode the refresh token manually
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Extract user info from the decoded token
            user_id = decoded_token.get('user_id')  # Adjust based on your token payload
            user = CustomUser.objects.get(id=user_id)

            # Optionally, handle the token blacklisting or any logout logic here
            print(f"Authenticated user: {user}")

        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
