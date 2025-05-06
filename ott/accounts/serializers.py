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
from exception import CustomAPIException
User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'phone_number', 'gender', 'birthdate','email', 'passcode']
        # read_only_fields = ['phone_number']  # prevent changing phone
    
    def create_admin(self, validated_data):
        print(validated_data)
        hashed =  bcrypt.hashpw(validated_data["passcode"].encode(), bcrypt.gensalt())
        passcode = hashed.decode()
        return CustomUser.objects.create_superuser(
            username=f"admin_{validated_data['fullname'].split()[0]}",
            phone_number=validated_data['phone_number'],
            fullname=validated_data['fullname'],
            gender=validated_data['gender'],
            birthdate=validated_data['birthdate'],
            email=validated_data['email'],  # Optional: fill if needed
            passcode=passcode,
            password=validated_data['passcode'],  # assuming passcode is treated as password
        )
    def update(self, instance, validated_data):
        print(instance.new_user)
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.passcode = validated_data.get('passcode', instance.passcode)
        instance.new_user=False
        instance.save()
        return instance
        
class MobileSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10)

    def validate_phone_number(self, value):
        return value
        
class VerifyPasscodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    passcode = serializers.CharField(max_length=128, required=False, allow_blank=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        passcode = data.get('passcode')

        # Retrieve user by phone number
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            raise CustomAPIException("Phone number not found.", status_code=404)

        if passcode:
            if not user.passcode:
                raise CustomAPIException("Passcode is not set for this user.", status_code=400)
            if not bcrypt.checkpw(passcode.encode(), user.passcode.encode()):
                raise CustomAPIException("Invalid passcode.", status_code=401)
            data['login_type'] = 'passcode'
        else:
            raise CustomAPIException('Passcode not found.',status_code=404)
        data['user'] = user
        return data


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp = attrs.get('otp')

        try:
            user = CustomUser.objects.filter(phone_number=phone_number).first()
            if not user:
                raise CustomAPIException("User not found.", status_code=404)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        print(user.otp,otp)
        # Check OTP
        if user.otp != otp:
            raise CustomAPIException("Invalid OTP.", status_code=400)

        if user.otp_expires and user.otp_expires < timezone.now():
            raise CustomAPIException("OTP has expired.", status_code=410)
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
            
            user = CustomUser.objects.filter(phone_number=phone_number).first()
            if user.passcode:
                raise CustomAPIException("Passcode already created successfully.", status_code=404)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        hashed = bcrypt.hashpw(passcode.encode(), bcrypt.gensalt())
        user.passcode = hashed.decode()
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'fullname', 'email', 'gender']

class ChangePasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    old_passcode = serializers.CharField(required=True)
    new_passcode = serializers.CharField(required=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        old_passcode = attrs.get('old_passcode')
        new_passcode = attrs.get('new_passcode')

        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            raise CustomAPIException("This phone number is not registered or not verified.", status_code=404)

        if not bcrypt.checkpw(old_passcode.encode(), user.passcode.encode()):
            raise CustomAPIException("Old passcode is incorrect.", status_code=401)

        if len(new_passcode) < 4:
            raise CustomAPIException("New passcode must be at least 4 characters long.", status_code=400)

        attrs['user'] = user
        return attrs