"""
URL configuration for core project.
Number Duel - Django Backend API Routes
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/auth/', include('accounts.urls')),  # Authentication endpoints
    path('api/game/', include('game.urls')),      # Game & Room endpoints
]
