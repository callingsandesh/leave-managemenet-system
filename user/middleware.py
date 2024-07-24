# userauth/middleware.py
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access')
        if access_token:
            try:
                validated_token = JWTAuthentication().get_validated_token(access_token)
                request.user = JWTAuthentication().get_user(validated_token)
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            except AuthenticationFailed:
                request.user = None
