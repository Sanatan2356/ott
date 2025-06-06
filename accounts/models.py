from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    
    # Make username optional by allowing null and blank
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    fullname = models.CharField(max_length=255,null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=60, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    passcode = models.CharField(max_length=10, blank=True, null=True)
    new_user = models.BooleanField(default=True)

    #  New fields for OTP functionality
    otp = models.CharField(max_length=6, blank=True, null=True)  # OTP field, store OTP
    otp_expires = models.DateTimeField(blank=True, null=True)  # OTP expiration time
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def is_otp_valid(self):
        """Check if OTP is still valid (not expired)"""
        if self.otp_expires and timezone.now() < self.otp_expires:
            return True
        return False
    def __str__(self):
        return self.username
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self,username, phone_number, fullname,email, birthdate, gender):
        if not phone_number:
            raise ValueError("Users must have a phone number")
        user = self.model(
            username=username,
            phone_number=phone_number,
            fullname=fullname,
            email=email,
            birthdate=birthdate,
            gender=gender,
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, fullname, birthdate, gender, password):
        user = self.create_user(phone_number, fullname, birthdate, gender)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class UserToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.phone_number}"
    
