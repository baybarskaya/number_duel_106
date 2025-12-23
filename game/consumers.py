import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Transaction, GameSession
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class GameConsumer(AsyncWebsocketConsumer):
    disconnect_timers = {}  # Class variable for disconnect tracking
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_id}'
        self.user_id = self.scope['user'].id

        # Odaya bağlan
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        print(f"🔌 WebSocket bağlandı: User {self.user_id}, Room {self.room_id}")

        # Disconnect timer varsa iptal et (reconnect durumu)
        timer_key = f"{self.room_id}_{self.user_id}"
        if timer_key in self.disconnect_timers:
            print(f"⏱️ Disconnect timer iptal edildi (reconnect): User {self.user_id}")
            self.disconnect_timers[timer_key].cancel()
            del self.disconnect_timers[timer_key]

        # Oyun verilerini başlat (Sadece ilk bağlanan için değil, oda dolduğunda)
        if await self.is_room_full():
            # GameSession var mı kontrol et, yoksa başlat
            game_exists = await self.game_session_exists()
            if not game_exists:
                # İlk kez oyun başlıyor - bahisleri çek!
                success = await self.lock_bets()
                if success:
                    await self.start_game()
                else:
                    await self.send(text_data=json.dumps({
                        'error': 'Bahis kilitlenemedi! Oyun başlatılamıyor.'
                    }))
            else:
                # Mevcut oyun durumunu gönder
                await self.send_current_game_state()

    async def disconnect(self, close_code):
        print(f"🔌 WebSocket koptu: User {self.user_id}, Room {self.room_id}, Code: {close_code}")
        
        try:
            game_state = await self.get_game_state()
            
            if not game_state:
                # Oyun henüz başlamamış - odayı OPEN'a çevir
                print(f"⚠️ Oyun başlamamış, oda OPEN'a çevriliyor")
                await self.reset_room_and_refund()
            else:
                # Oyun başlamış - 30 saniye timer
                if not game_state.get('winner_id'):
                    print(f"⏱️ 30 saniye disconnect timer başlatıldı: User {self.user_id}")
                    
                    import asyncio
                    timer_key = f"{self.room_id}_{self.user_id}"
                    timer = asyncio.create_task(self.handle_disconnect_timeout())
                    self.disconnect_timers[timer_key] = timer
                    
        except Exception as e:
            print(f"❌ Disconnect handling hatası: {str(e)}")
            import traceback
            traceback.print_exc()
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'guess':
            guess = int(data.get('number'))
            await self.handle_guess(guess)
        
        elif action == 'leave_game':
            # Manuel ayrılma
            print(f"👋 Manuel ayrılma isteği: User {self.user_id}")
            await self.handle_manual_leave()

    async def start_game(self):
        """
        Oyunu başlat - SADECE BİR KEZ çağrılmalı
        İki consumer instance olsa bile, sadece bir GameSession oluşturulmalı
        """
        print(f"\n🎮 start_game() çağrıldı - Room ID: {self.room_id}")
        
        # ÖNCE: Zaten bir GameSession var mı kontrol et
        existing_game = await self.get_game_state()
        if existing_game:
            print(f"⚠️ GameSession zaten var! Yeni oluşturulmayacak.")
            print(f"   Target: {existing_game['target_number']}, Turn: {existing_game['current_turn_name']}")
            # Mevcut oyun durumunu client'lara gönder
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': f'🎮 Oyun devam ediyor!',
                    'turn': existing_game['current_turn_id'],
                    'turn_name': existing_game['current_turn_name'],
                    'event': 'START'
                }
            )
            return
        
        # YENİ: GameSession oluştur
        target_number = random.randint(1, 100)
        
        # Yazı-tura ile başlayacak oyuncuyu seç
        room_data = await self.get_room_players()
        players = [room_data['creator_id'], room_data['player2_id']]
        starting_player_id = random.choice(players)
        
        # GameSession oluştur (veritabanında state tut) - ATOMIC!
        success = await self.create_game_session(target_number, starting_player_id)
        
        if not success:
            print(f"❌ GameSession oluşturulamadı!")
            return
        
        print(f"✅ GameSession oluşturuldu:")
        print(f"   Target Number: {target_number}")
        print(f"   Starting Player ID: {starting_player_id}")
        
        # Başlayan oyuncunun adını al
        starting_player_name = await self.get_username(starting_player_id)
        print(f"   Starting Player Name: {starting_player_name}")
        
        # Oyuncuların güncel bakiyelerini al
        player_balances = await self.get_player_balances()
        print(f"   Bakiye bilgileri hazırlandı")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': f'🎮 Oyun başladı! Gizli sayı 1-100 arasında seçildi.',
                'turn': starting_player_id,
                'turn_name': starting_player_name,
                'event': 'START',
                'balances': player_balances
            }
        )
        
        print(f"📤 START mesajı gönderildi (bakiye bilgileri dahil)\n")

    async def handle_guess(self, guess):
        user_id = self.scope['user'].id
        username = self.scope['user'].username
        
        print(f"\n=== TAHMIN KONTROLÜ ===")
        print(f"Tahmin yapan: {username} (ID: {user_id}, Tip: {type(user_id)})")
        print(f"Tahmin: {guess}")
        
        # VERİTABANINDAN oyun durumunu al
        game_state = await self.get_game_state()
        
        if not game_state:
            print(f"❌ Oyun bulunamadı!")
            await self.send(text_data=json.dumps({'error': 'Oyun bulunamadı!'}))
            return
        
        print(f"Sıradaki: {game_state['current_turn_name']} (ID: {game_state['current_turn_id']}, Tip: {type(game_state['current_turn_id'])})")
        print(f"Eşit mi? {user_id} == {game_state['current_turn_id']} → {user_id == game_state['current_turn_id']}")
        
        # Sıra kontrolü (veritabanından)
        if user_id != game_state['current_turn_id']:
            print(f"❌ Sıra kontrolü başarısız!")
            print(f"======================\n")
            
            # Sadece hata yapan kullanıcıya gönder, diğerine gönderme
            await self.send(text_data=json.dumps({
                'error': f'Lütfen sıranı bekle. Şu an sıra: {game_state["current_turn_name"]}'
            }))
            return
        
        print(f"✅ Sıra kontrolü başarılı!")
        print(f"======================\n")

        response_msg = ""
        event = "CONTINUE"
        target_number = game_state['target_number']

        # Tahmin kontrolü
        if guess < target_number:
            response_msg = f"📈 {username}: {guess} → Daha YUKARI!"
        elif guess > target_number:
            response_msg = f"📉 {username}: {guess} → Daha AŞAĞI!"
        else:
            response_msg = f"🎉 {username} doğru sayıyı buldu: {guess}"
            event = "WINNER"
            await self.finish_game(user_id)

        # Sırayı değiştir ve VERİTABANINA kaydet
        players = await self.get_room_players()
        next_player_id = players['player2_id'] if user_id == players['creator_id'] else players['creator_id']
        next_player_name = await self.get_username(next_player_id)
        
        # History'ye ekle ve sırayı güncelle
        await self.update_game_state(
            guess=guess,
            guesser_name=username,
            response=response_msg,
            next_turn_id=next_player_id if event != 'WINNER' else None,
            winner_id=user_id if event == 'WINNER' else None
        )

        # Tüm oyunculara gönder
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': response_msg,
                'last_guess': guess,
                'guesser_name': username,
                'guesser_id': user_id,
                'turn': next_player_id if event != 'WINNER' else None,
                'turn_name': next_player_name if event != 'WINNER' else None,
                'event': event,
                'winner_id': user_id if event == 'WINNER' else None,
                'reason': 'normal' if event == 'WINNER' else None
            }
        )

    async def game_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def is_room_full(self):
        room = Room.objects.get(id=self.room_id)
        return room.status == 'FULL'

    @database_sync_to_async
    def get_room_players(self):
        room = Room.objects.get(id=self.room_id)
        return {'creator_id': room.creator.id, 'player2_id': room.player2.id}

    @database_sync_to_async
    def get_username(self, user_id):
        """Kullanıcı adını getir"""
        user = User.objects.get(id=user_id)
        return user.username
    
    @database_sync_to_async
    def reset_room_and_refund(self):
        """
        Oyun başlamadan oyuncu ayrıldıysa:
        - Odayı OPEN durumuna çevir
        - player2'yi kaldır
        - Bahisleri iade et
        """
        from django.db import transaction as db_transaction
        from decimal import Decimal
        
        try:
            with db_transaction.atomic():
                room = Room.objects.select_for_update().get(id=self.room_id)
                
                # Bahis kilitli mi kontrol et
                bet_locked = Transaction.objects.filter(
                    description__contains=f"Oda #{room.id} bahis kilidi"
                ).exists()
                
                if bet_locked and room.status == 'FULL':
                    # Bahisleri iade et
                    bet = Decimal(str(room.bet_amount))
                    creator = User.objects.select_for_update().get(id=room.creator.id)
                    
                    if room.player2:
                        player2 = User.objects.select_for_update().get(id=room.player2.id)
                        
                        creator.balance += bet
                        player2.balance += bet
                        creator.save()
                        player2.save()
                        
                        # İade transaction'ları
                        Transaction.objects.create(
                            user=creator,
                            amount=bet,
                            description=f"Oda #{room.id} bahis iadesi (oyuncu ayrıldı)"
                        )
                        Transaction.objects.create(
                            user=player2,
                            amount=bet,
                            description=f"Oda #{room.id} bahis iadesi (oyuncu ayrıldı)"
                        )
                        
                        print(f"💰 Bahisler iade edildi: {bet} x 2 oyuncu")
                
                # Odayı OPEN'a çevir
                room.player2 = None
                room.status = 'OPEN'
                room.save()
                
                print(f"✅ Oda OPEN durumuna çevrildi: Room #{room.id}")
                
        except Exception as e:
            print(f"❌ reset_room_and_refund hatası: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def handle_manual_leave(self):
        """
        Kullanıcı 'Lobiye Dön' butonuna bastı
        """
        print(f"👋 Manuel ayrılma: User {self.user_id}, Room {self.room_id}")
        
        game_state = await self.get_game_state()
        
        if not game_state:
            # Oyun başlamamış - reset ve iade
            print(f"   Oyun başlamamış, bahisler iade edilecek")
            await self.reset_room_and_refund()
        else:
            # Oyun başlamış - diğer oyuncuyu kazandır
            if not game_state.get('winner_id'):
                print(f"   Oyun başlamış, diğer oyuncu kazanacak")
                
                room_data = await self.get_room_players()
                other_player_id = (
                    room_data['player2_id'] 
                    if self.user_id == room_data['creator_id'] 
                    else room_data['creator_id']
                )
                
                await self.finish_game(other_player_id, reason='manual_leave')
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_message',
                        'message': '🏆 Rakibiniz oyundan ayrıldı. Kazandınız!',
                        'event': 'WINNER',
                        'winner_id': other_player_id,
                        'reason': 'manual_leave'
                    }
                )
            else:
                print(f"   Oyun zaten bitti")
    
    @database_sync_to_async
    def get_player_balances(self):
        """
        Her oyuncuya kendi bakiye bilgisini döndür
        """
        room = Room.objects.get(id=self.room_id)
        creator = User.objects.get(id=room.creator.id)
        player2 = User.objects.get(id=room.player2.id)
        bet = room.bet_amount
        
        return {
            'creator': {
                'user_id': creator.id,
                'current': float(creator.balance),
                'start': float(creator.balance + bet),
                'bet': float(bet)
            },
            'player2': {
                'user_id': player2.id,
                'current': float(player2.balance),
                'start': float(player2.balance + bet),
                'bet': float(bet)
            }
        }
    
    @database_sync_to_async
    def game_session_exists(self):
        """GameSession var mı kontrol et"""
        return GameSession.objects.filter(room_id=self.room_id).exists()
    
    @database_sync_to_async
    def create_game_session(self, target_number, starting_player_id):
        """
        Yeni GameSession oluştur - ATOMIC ve TEK SEFER
        get_or_create kullanarak aynı oda için sadece bir GameSession olmasını garanti et
        """
        from django.db import transaction as db_transaction
        
        try:
            with db_transaction.atomic():
                room = Room.objects.get(id=self.room_id)
                starting_player = User.objects.get(id=starting_player_id)
                
                # get_or_create: Varsa getir, yoksa oluştur
                game_session, created = GameSession.objects.get_or_create(
                    room=room,
                    defaults={
                        'target_number': target_number,
                        'current_turn': starting_player,
                        'history': []
                    }
                )
                
                if created:
                    print(f"✅ YENİ GameSession oluşturuldu: ID={game_session.id}")
                else:
                    print(f"⚠️ GameSession ZATEN VAR: ID={game_session.id}, mevcut kullanılıyor")
                
                return True
        except Exception as e:
            print(f"❌ GameSession oluşturma HATASI: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    @database_sync_to_async
    def get_game_state(self):
        """Veritabanından oyun durumunu al"""
        try:
            game = GameSession.objects.select_related('current_turn').get(room_id=self.room_id)
            
            print(f"📊 GameSession State:")
            print(f"   Room ID: {self.room_id}")
            print(f"   Target: {game.target_number}")
            print(f"   Current Turn: {game.current_turn.username} (ID: {game.current_turn.id})")
            print(f"   History Count: {len(game.history)}")
            
            return {
                'target_number': game.target_number,
                'current_turn_id': game.current_turn.id,
                'current_turn_name': game.current_turn.username,
                'history': game.history,
                'winner_id': game.winner_id if game.winner else None
            }
        except GameSession.DoesNotExist:
            print(f"❌ GameSession bulunamadı! Room ID: {self.room_id}")
            return None
    
    @database_sync_to_async
    def update_game_state(self, guess, guesser_name, response, next_turn_id, winner_id=None):
        """Oyun durumunu güncelle"""
        from django.db import transaction as db_transaction
        
        with db_transaction.atomic():
            game = GameSession.objects.select_for_update().get(room_id=self.room_id)
            
            # History'ye ekle
            history_entry = {
                'guess': guess,
                'guesser': guesser_name,
                'response': response,
                'timestamp': timezone.now().isoformat()
            }
            game.history.append(history_entry)
            
            # Sırayı güncelle
            if next_turn_id:
                game.current_turn_id = next_turn_id
            
            # Kazanan varsa kaydet
            if winner_id:
                game.winner_id = winner_id
                game.ended_at = timezone.now()
            
            game.save()
    
    @database_sync_to_async
    def send_current_game_state(self):
        """Mevcut oyun durumunu yeni bağlanan kullanıcıya gönder"""
        try:
            game = GameSession.objects.select_related('current_turn').get(room_id=self.room_id)
            return {
                'current_turn_id': game.current_turn.id,
                'current_turn_name': game.current_turn.username,
                'history_count': len(game.history)
            }
        except GameSession.DoesNotExist:
            return None
    
    async def handle_disconnect_timeout(self):
        """
        30 saniye bekle, eğer reconnect olmazsa diğer oyuncuya kazandır
        """
        import asyncio
        
        try:
            # 30 saniye bekle
            await asyncio.sleep(30)
            
            print(f"⏰ 30 saniye doldu! User {self.user_id} geri dönmedi.")
            print(f"   Diğer oyuncu kazanacak...")
            
            # Diğer oyuncuyu bul
            room_data = await self.get_room_players()
            other_player_id = (
                room_data['player2_id'] 
                if self.user_id == room_data['creator_id'] 
                else room_data['creator_id']
            )
            
            # Diğer oyuncuyu kazanan yap
            await self.finish_game(other_player_id, reason='disconnect')
            
            # Tüm oyunculara bildir
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': f'🚫 Rakip 30 saniye bağlantısız kaldı. Oyunu kazandınız!',
                    'event': 'WINNER',
                    'winner_id': other_player_id,
                    'reason': 'disconnect'
                }
            )
            
        except asyncio.CancelledError:
            # Timer iptal edildi (reconnect oldu)
            print(f"✅ Timer iptal edildi, user {self.user_id} geri döndü")
        except Exception as e:
            print(f"❌ Disconnect timeout hatası: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @database_sync_to_async
    def lock_bets(self):
        """
        Oyun başlarken bahisleri kilitle (çek)
        """
        from django.db import transaction as db_transaction
        from decimal import Decimal
        
        try:
            with db_transaction.atomic():
                room = Room.objects.select_for_update().get(id=self.room_id)
                
                # Zaten kilit var mı kontrol et
                if Transaction.objects.filter(
                    description__contains=f"Oda #{room.id} bahis kilidi"
                ).exists():
                    print(f"⚠️ Bahisler zaten kilitli: Room {self.room_id}")
                    return True
                
                creator = User.objects.select_for_update().get(id=room.creator.id)
                player2 = User.objects.select_for_update().get(id=room.player2.id)
                bet = Decimal(str(room.bet_amount))
                
                # Bakiye kontrolleri
                if creator.balance < bet:
                    print(f"❌ {creator.username} bakiyesi yetersiz!")
                    return False
                
                if player2.balance < bet:
                    print(f"❌ {player2.username} bakiyesi yetersiz!")
                    return False
                
                # Bahisleri çek
                creator.balance -= bet
                player2.balance -= bet
                creator.save()
                player2.save()
                
                # Transaction kayıtları
                Transaction.objects.create(
                    user=creator,
                    amount=-bet,
                    description=f"Oda #{room.id} bahis kilidi"
                )
                
                Transaction.objects.create(
                    user=player2,
                    amount=-bet,
                    description=f"Oda #{room.id} bahis kilidi"
                )
                
                print(f"✅ Bahisler kilitlendi: {bet} puan x 2 oyuncu")
                print(f"   {creator.username}: {creator.balance + bet} → {creator.balance}")
                print(f"   {player2.username}: {player2.balance + bet} → {player2.balance}")
                
                return True
                
        except Exception as e:
            print(f"❌ Bahis kilitleme hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    @database_sync_to_async
    def finish_game(self, winner_id, reason='normal'):
        """
        Oyun bitişinde bakiye transferini gerçekleştir
        reason: 'normal' (doğru tahmin) veya 'disconnect' (rakip ayrıldı)
        """
        from django.db import transaction as db_transaction
        from decimal import Decimal
        
        try:
            with db_transaction.atomic():
                # Odayı kilitle (race condition önlemi)
                room = Room.objects.select_for_update().get(id=self.room_id)
                
                # Zaten bitmişse tekrar işlem yapma
                if room.status == 'FINISHED':
                    print(f"⚠️ Oyun zaten bitti: Room {self.room_id}")
                    return
                
                # Kazanan ve kaybedeni belirle
                winner = User.objects.select_for_update().get(id=winner_id)
                loser_id = room.player2.id if winner_id == room.creator.id else room.creator.id
                loser = User.objects.select_for_update().get(id=loser_id)
                
                bet = Decimal(str(room.bet_amount))
                
                # Bahisler zaten kilitlendiyse, kazanana 2x ver
                # (Çünkü her iki oyuncudan da çekilmişti)
                winner.balance += (bet * 2)
                
                # İstatistikleri güncelle
                winner.total_wins += 1
                winner.total_games += 1
                loser.total_games += 1
                
                winner.save()
                loser.save()
                
                print(f"📊 İstatistikler güncellendi:")
                print(f"   {winner.username}: {winner.total_wins} win / {winner.total_games} game (Win rate: {winner.win_rate}%)")
                print(f"   {loser.username}: {loser.total_wins} win / {loser.total_games} game (Win rate: {loser.win_rate}%)")
                
                # Transaction kayıtları
                if reason == 'disconnect':
                    Transaction.objects.create(
                        user=winner,
                        amount=(bet * 2),
                        description=f"Oda #{room.id} kazancı - Rakip 30sn bağlantısız"
                    )
                    print(f"🏆 Disconnect kazancı: {winner.username} +{bet * 2}")
                elif reason == 'manual_leave':
                    Transaction.objects.create(
                        user=winner,
                        amount=(bet * 2),
                        description=f"Oda #{room.id} kazancı - Rakip oyunu terketti"
                    )
                    print(f"🏆 Manuel ayrılma kazancı: {winner.username} +{bet * 2}")
                else:
                    Transaction.objects.create(
                        user=winner,
                        amount=(bet * 2),
                        description=f"Oda #{room.id} kazancı - Rakip: {loser.username}"
                    )
                    print(f"🏆 Normal kazanç: {winner.username} +{bet * 2}")
                
                # Oda durumunu güncelle
                room.status = 'FINISHED'
                room.save()
                
                # GameSession'ı güncelle
                try:
                    game = GameSession.objects.get(room_id=self.room_id)
                    game.winner_id = winner_id
                    game.ended_at = timezone.now()
                    game.save()
                except GameSession.DoesNotExist:
                    pass
                
                print(f"✅ Oyun bitti: Room {self.room_id}, Kazanan: {winner.username}")
                
        except Exception as e:
            print(f"❌ finish_game hatası: {str(e)}")
            import traceback
            traceback.print_exc()