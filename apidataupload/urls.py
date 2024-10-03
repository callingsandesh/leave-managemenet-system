from django.contrib import admin
from django.urls import path , include
from apidataupload import views


urlpatterns = [
    path('api/',views.handle_api_data,name='handle_api_data' ),
    path('upload/', views.upload_file, name='upload_file'),
    path('navigation/', views.navigation, name='navigation'),
    path('', views.index, name='index')
]