from django.db import transaction
from .models import Transaction, Room

def process_game_results(room_id, winner_id):
    with transaction.atomic():
        room = Room.objects.select_for_update().get(id=room_id)
        bet = room.bet_amount
        
        players = [room.creator, room.player2]
        winner = next(p for p in players if p.id == winner_id)
        loser = next(p for p in players if p.id != winner_id)
        winner.balance += bet
        winner.save()
        
        loser.balance -= bet
        loser.save()

        Transaction.objects.create(user=winner, amount=bet, description=f"Oyun Kazanıldı: Oda #{room.id}")
        Transaction.objects.create(user=loser, amount=-bet, description=f"Oyun Kaybedildi: Oda #{room.id}")
        
        room.status = 'FINISHED'
        room.save()