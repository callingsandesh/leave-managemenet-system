# user/decorator.py
import jwt
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

def authenticated_user(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # First, check for session-based authentication
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        # Check for JWT token in Authorization header
        token = request.META.get('HTTP_AUTHORIZATION')
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
            try:
                # Validate the token
                validated_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = validated_token.get('user_id')
                request.user = get_user_model().objects.get(id=user_id)
                return view_func(request, *args, **kwargs)
            except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist) as e:
                # Redirect to login on token issues
                return redirect(reverse('login'))  # Adjust the name to match your URL pattern
        else:
            # Redirect to login if no valid credentials
            return redirect(reverse('login'))  # Adjust the name to match your URL pattern

    return _wrapped_view
