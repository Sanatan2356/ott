# accounts/serializers.py
import random
import bcrypt
from datetime import datetime,timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import CustomUser
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from django.contrib.auth.hashers import check_password
User = get_user_model()






class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'phone_number', 'gender', 'birthdate', 'passcode']
        # read_only_fields = ['phone_number']  # prevent changing phone
    def create_admin(self, validated_data):
        return CustomUser.objects.create_superuser(
            username=f"admin_{validated_data['fullname'].split()[0]}",
            phone_number=validated_data['phone_number'],
            fullname=validated_data['fullname'],
            gender=validated_data['gender'],
            birthdate=validated_data['birthdate'],
            email='',  # Optional: fill if needed
            password=validated_data['passcode'],  # assuming passcode is treated as password
        )
    def update(self, instance, validated_data):
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.passcode = validated_data.get('passcode', instance.passcode)
        instance.save()
        return instance
        
class MobileSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10)

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    passcode = serializers.CharField(max_length=128, required=False, allow_blank=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        passcode = data.get('passcode')

        # Retrieve user by phone number
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            raise NotFound("Phone number not found.")

        # If passcode is provided, validate it
        if passcode:
            if not user.passcode:
                raise ValidationError("Passcode is not set for this user.")
            if not bcrypt.checkpw(passcode.encode(), user.passcode.encode()):
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
