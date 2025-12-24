from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import Room, GlobalSettings, Transaction, GameSession

User = get_user_model()

# Global Ayarlar
@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('min_bet', 'max_bet', 'bet_step')
    
    def has_add_permission(self, request):
        return not GlobalSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        ('Bahis Limitleri', {
            'fields': ('min_bet', 'max_bet', 'bet_step'),
            'description': 'Oyun odalarında kullanılacak bahis limitleri'
        }),
    )

# Kullanıcı Yönetimi
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 
        'balance', 
        'total_games',
        'total_wins',
        'win_rate_display',
        'is_active', 
        'is_staff', 
        'birth_date'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'total_games')
    ordering = ('-balance',)
    readonly_fields = ('total_games', 'total_wins', 'win_rate_display', 'date_joined', 'last_login')
    
    def win_rate_display(self, obj):
        rate = obj.win_rate
        if rate >= 60:
            color = 'green'
        elif rate >= 40:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, rate
        )
    win_rate_display.short_description = 'Kazanma Oranı'
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('username', 'email', 'birth_date', 'is_verified')
        }),
        ('Bakiye ve İstatistikler', {
            'fields': ('balance', 'total_games', 'total_wins', 'win_rate_display')
        }),
        ('Yetkiler', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Önemli Tarihler', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )


# Hesap Hareketleri
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'amount_display',
        'description',
        'created_at'
    )
    list_filter = (
        'created_at',
        'user',
    )
    search_fields = ('user__username', 'description')
    date_hierarchy = 'created_at'
    
    def amount_display(self, obj):
        if obj.amount > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">+{}</span>',
                obj.amount
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                obj.amount
            )
    amount_display.short_description = 'Miktar'
    amount_display.admin_order_field = 'amount'


# Oyun Odaları
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'bet_amount',
        'status_display',
        'player_count',
        'creator',
        'player2',
        'created_at',
    )
    list_filter = ('status', 'bet_amount', 'created_at')
    search_fields = ('name', 'creator__username', 'player2__username')
    date_hierarchy = 'created_at'
    
    def status_display(self, obj):
        colors = {
            'OPEN': 'blue',
            'FULL': 'orange',
            'FINISHED': 'green'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Durum'
    
    def player_count(self, obj):
        count = 1
        if obj.player2:
            count = 2
        return f"{count}/2"
    player_count.short_description = 'Oyuncular'


# Oyun Oturumları
@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'room_name',
        'bet_amount_display',
        'winner',
        'loser_display',
        'turn_count_display',
        'duration_display',
        'started_at',
    )
    list_filter = ('started_at', 'winner', 'ended_at')
    search_fields = ('room__name', 'winner__username', 'room__creator__username', 'room__player2__username')
    readonly_fields = ('started_at', 'ended_at', 'history', 'target_number', 'turn_count_display', 'duration_display')
    
    def room_name(self, obj):
        return f"#{obj.room.id} - {obj.room.name}"
    room_name.short_description = 'Oda'
    
    def bet_amount_display(self, obj):
        return format_html('<strong>{}</strong> puan', obj.bet_amount)
    bet_amount_display.short_description = 'Bahis'
    
    def loser_display(self, obj):
        loser = obj.loser
        if loser:
            return format_html('<span style="color: red;">{}</span>', loser.username)
        return '-'
    loser_display.short_description = 'Kaybeden'
    
    def turn_count_display(self, obj):
        return f"{obj.turn_count} tahmin"
    turn_count_display.short_description = 'Tur Sayısı'
    
    def duration_display(self, obj):
        return obj.game_duration
    duration_display.short_description = 'Süre'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('history_display',)
        return self.readonly_fields
    
    def history_display(self, obj):
        if not obj.history:
            return "Henüz tahmin yapılmadı"
        
        html = '<table style="width:100%; border-collapse: collapse; margin-top: 10px;">'
        html += '<tr style="background: #417690; color: white;"><th style="padding: 8px;">#</th><th>Oyuncu</th><th>Tahmin</th><th>Sonuç</th><th>Zaman</th></tr>'
        
        for idx, entry in enumerate(obj.history, 1):
            bg_color = '#f9f9f9' if idx % 2 == 0 else 'white'
            html += f'<tr style="border-bottom: 1px solid #ddd; background: {bg_color};">'
            html += f'<td style="padding: 8px; text-align: center;"><strong>{idx}</strong></td>'
            html += f'<td style="padding: 8px;"><strong>{entry.get("guesser", "")}</strong></td>'
            html += f'<td style="padding: 8px; text-align: center;">{entry.get("guess", "")}</td>'
            html += f'<td style="padding: 8px;">{entry.get("response", "")[:60]}</td>'
            html += f'<td style="padding: 8px;"><small>{entry.get("timestamp", "")[:19]}</small></td>'
            html += f'</tr>'
        
        html += '</table>'
        html += f'<p style="margin-top: 10px;"><strong>Toplam Tahmin:</strong> {len(obj.history)}</p>'
        return format_html(html)
    history_display.short_description = 'Oyun Geçmişi (Detaylı)'


# Register İşlemleri
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
