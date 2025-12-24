from django.db import models

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

class GlobalSettings(models.Model):
    min_bet = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    max_bet = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    bet_step = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)

    class Meta:
        verbose_name = "Global Settings"
        verbose_name_plural = "Global Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

class Room(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open (Waiting)'),
        ('FULL', 'Full (In Progress)'),
        ('FINISHED', 'Finished'),
    )

    name = models.CharField(max_length=50)
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_rooms")
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="joined_rooms")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.bet_amount} Point"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.amount}"

    class Meta:
        ordering = ['-created_at']


class GameSession(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name="game_session")
    target_number = models.IntegerField()
    current_turn = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_games")
    history = models.JSONField(default=list)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_games")

    def __str__(self):
        return f"Game #{self.id} - Room: {self.room.name}"

    class Meta:
        ordering = ['-started_at']
    
    @property
    def loser(self):
        if not self.winner:
            return None
        if self.winner == self.room.creator:
            return self.room.player2
        return self.room.creator
    
    @property
    def bet_amount(self):
        return self.room.bet_amount
    
    @property
    def turn_count(self):
        return len(self.history) if self.history else 0

    @property
    def game_duration(self):
        if self.ended_at and self.started_at:
            delta = self.ended_at - self.started_at
            minutes = int(delta.total_seconds() / 60)
            seconds = int(delta.total_seconds() % 60)
            return f"{minutes}:{seconds:02d}"
        return "Devam ediyor"