# accounts/serializers.py
import random
import bcrypt
from datetime import datetime,timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import CustomUser
User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['fullname', 'phone_number', 'gender', 'birthdate', 'passcode']

    def create(self, validated_data):
        # Check if username is provided, else generate a default one or leave it blank
        username = validated_data.get('username', None)
        
        if not username:
            # If no username is provided, we can either leave it as None or generate a default username
            # Optionally, generate a username (e.g., based on the fullname)
            username = f"user_{validated_data['fullname'].split()[0]}"  # You can customize this logic

        # Ensure that we pass a username to the `create_user` method
        user = User.objects.create_user(
            username=username,  # Use the generated or provided username
            **validated_data  # This will pass the rest of the fields
        )
        return user
    
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    passcode = serializers.CharField(max_length=10, required=False, allow_blank=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        passcode = data.get('passcode')

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            raise NotFound("Phone number not found.")

        if passcode:
            # Password-based login
            if not user.passcode or user.passcode != passcode:
                raise ValidationError("Invalid passcode.")
            data['login_type'] = 'passcode'
        else:
            data['login_type'] = 'otp'

        data['user'] = user
        return data


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp = attrs.get('otp')

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        # Check OTP
        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        # Check expiration
        if user.otp_expires and user.otp_expires < timezone.now():
            raise serializers.ValidationError("OTP has expired.")

        attrs['user'] = user
        return attrs


class SetPasscodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    passcode = serializers.CharField(min_length=4, max_length=4)

    def validate_passcode(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Passcode must be numeric.")
        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        passcode = validated_data['passcode']

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        hashed = bcrypt.hashpw(passcode.encode(), bcrypt.gensalt())
        user.passcode = hashed.decode()
        user.save()
        return user
