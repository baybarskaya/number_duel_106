from django.urls import path
from .views import register_view, login_view, profile_view, balance_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', profile_view, name='profile'),
    path('balance/', balance_view, name='balance'),
]

