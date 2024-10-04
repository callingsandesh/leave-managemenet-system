# userauth/middleware.py
import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser

class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access')
        if access_token:
            try:
                validated_token = JWTAuthentication().get_validated_token(access_token)
                request.user = JWTAuthentication().get_user(validated_token)
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            except (InvalidToken, TokenError):
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
