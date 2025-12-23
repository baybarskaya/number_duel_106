from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, TransactionListView, LeaderboardView

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]

