from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class CustomUser(AbstractUser):
    # Yeni kayıt olan her kullanıcı 1000 birim ile başlar
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=1000.00,
        validators=[MinValueValidator(0)]
    )
    birth_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Oyun istatistikleri
    total_games = models.IntegerField(default=0)  # Toplam oynadığı oyun
    total_wins = models.IntegerField(default=0)   # Kazandığı oyun sayısı

    def __str__(self):
        return f"{self.username} ({self.balance} Point)"

    @property
    def is_adult(self):
        from datetime import date
        if not self.birth_date:
            return False
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age >= 18
    
    @property
    def win_rate(self):
        """Kazanma oranı (%)"""
        if self.total_games == 0:
            return 0
        return round((self.total_wins / self.total_games) * 100, 1)