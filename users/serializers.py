from rest_framework import serializers
from django.contrib.auth.models import User
from .utils import generate_otp
from .models import Profile
from django.core.mail import send_mail
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    profile_img = serializers.CharField(source='profile.profile_img', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile_img']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False}
        }
        
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile = instance.profile
            if not hasattr(instance, 'profile'):
                Profile.objects.create(user=instance, **profile_data)
            else:
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()

        return instance

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    profile_img = serializers.URLField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'profile_img']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        profile_img = validated_data.pop('profile_img', None)
        user = User.objects.create_user(**validated_data)

        user.is_active = False 
        user.save()

        otp_code = generate_otp()
        Profile.objects.create(
            user=user, 
            profile_img=profile_img, 
            otp=otp_code,
            otp_created_at=timezone.now()  
        )

        email_subject = 'Your OTP Code : '
        email_body = f'Your OTP Code Is : {otp_code} (Valid for 1 minutes)'
        send_mail(
            email_subject,
            email_body,
            'syednazmusshakib94@gmail.com', 
            [user.email]
        )
        
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

