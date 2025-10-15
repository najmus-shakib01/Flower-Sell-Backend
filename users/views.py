from .models import Profile
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .serializers import  UserSerializer, RegistrationSerializer, LoginSerializer
from django.shortcuts import get_object_or_404
from .utils import generate_otp
from django.core.mail import send_mail
from django.utils import timezone

#user dekar jonno
class UserAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(user)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#user register korar jonno
class RegisterAPIView(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save() 

            email_subject = 'Welcome To Our Platform!'
            email_body = render_to_string('welcome_email.html', {'username': user.username})

            email = EmailMultiAlternatives(email_subject, '', 'syednazmusshakib94@gmail.com', [user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()

            return Response({'detail': 'Check your email for confirmation'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#send opt
class ResendOTPApiView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'Error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=email)

        otp_code = generate_otp()

        print(f"[{email}] Saving OTP to DB: {otp_code}")
        user.profile.otp = otp_code
        user.profile.otp_created_at = timezone.now()  
        user.profile.save(update_fields=['otp', 'otp_created_at'])

        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP Code is: {otp_code} (Valid for 1 minutes)',
            from_email='syednazmusshakib94@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'Message': 'New OTP has been sent to your email'}, status=status.HTTP_200_OK)
    

#verify otp
class VerifyOTPApiView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'Error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=email)
        profile = user.profile

        print(f"[{email}] Received OTP: {otp}")
        print(f"[{email}] Actual OTP in DB: {profile.otp}")

        if profile.is_otp_expired():
            return Response({'Error': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        if str(profile.otp) == str(otp):
            user.is_active = True
            user.save(update_fields=['is_active'])

            profile.otp = None
            profile.otp_created_at = None
            profile.save(update_fields=['otp', 'otp_created_at'])

            return Response({'Message': 'Account activated successfully'}, status=status.HTTP_200_OK)

        return Response({'Error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    

#user login korar jonno
class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)

                return Response({
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email, 
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


#user logout korar jonno
class LogoutAPIView(APIView):
    def get(self, request):
        user = request.user
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)