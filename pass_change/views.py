from rest_framework.views import APIView
from .serializers import PasswordChangeSerializer, PasswordResetRequestSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str

class PasswordResetRequestAPIView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk)) 
                reset_link = f'https://flower-sell.vercel.app/reset_password/{uid}/{token}/'
                email_subject = 'Reset Your Password'
                email_body = render_to_string('reset_password_email.html', {'reset_link': reset_link})
                email = EmailMultiAlternatives(email_subject, '', to=[user.email])
                email.attach_alternative(email_body, 'text/html')
                email.send()
                return Response({'detail': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordChangeAPIView(APIView):
    def post(self, request, uid64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Invalid user or token.'}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None and default_token_generator.check_token(user, token):
            serializer = PasswordChangeSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'detail': 'Password has been changed successfully.'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Invalid token or user.'}, status=status.HTTP_400_BAD_REQUEST)