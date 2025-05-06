from django.urls import path
from .views import (SignUpView,UserProfileView,VerifyPasscodeView,OTPVerifyView,SetPasscodeView,
LogoutView,MobileVerifyView,AdminSignUpView,AdminAllUsersView,ChangePasscodeView)

urlpatterns = [
    path('verify-mobile/',MobileVerifyView.as_view(),name='verify-mobile'),
    path('create-admin/', AdminSignUpView.as_view(), name='admin-signup'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify-passcode/', VerifyPasscodeView.as_view(), name='verify-passcode'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('set-passcode', SetPasscodeView.as_view(), name='set-passcode'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('admin/all-users/', AdminAllUsersView.as_view(), name='admin-all-users'),
    path("change-passcode/", ChangePasscodeView.as_view(), name="change-passcode")
]
