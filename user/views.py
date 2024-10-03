from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.middleware.csrf import get_token

# user/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            response = redirect('/api/v1/dataupload/')  # Make sure the redirect URL is correct
            response.set_cookie('access', str(refresh.access_token))
            response.set_cookie('refresh', str(refresh))
            return response
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
        
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    response = render(request, 'login.html', {'message': 'Logged out successfully'})
    #response = JsonResponse({'message': 'Logged out successfully'})
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    return response
