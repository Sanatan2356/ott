from django.urls import path
from .views import SignUpView,LoginView,OTPVerifyView,SetPasscodeView,LogoutView,MobileVerifyView,AdminSignUpView

urlpatterns = [
    path('verify-mobile/',MobileVerifyView.as_view(),name='verify-mobile'),
    path('create-admin/', AdminSignUpView.as_view(), name='admin-signup'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('set-passcode', SetPasscodeView.as_view(), name='set-passcode'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
