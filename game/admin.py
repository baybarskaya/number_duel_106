from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Room, GlobalSettings, Transaction, GameSession

User = get_user_model()


# Global Ayarlar
@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('min_bet', 'max_bet', 'bet_step')


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'balance', 'is_active', 'is_staff', 'birth_date')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')
    ordering = ('-balance',)  # En zengin oyuncular üstte


# Hesap Hareketleri
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'description')


# Oyun Odaları
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'bet_amount',
        'status',
        'creator',
        'player2',
        'created_at',
    )
    list_filter = ('status', 'bet_amount')
    search_fields = ('name', 'creator__username')


# Oyun Oturumları
@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'winner', 'started_at', 'ended_at')
    list_filter = ('started_at', 'winner')
    search_fields = ('room__name', 'winner__username')
    readonly_fields = ('started_at', 'history')


# Register İşlemleri
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
