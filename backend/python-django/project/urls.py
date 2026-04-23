from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    # 👇 THIS IS THE IMPORTANT LINE
    path('', include('app.urls')),
]
