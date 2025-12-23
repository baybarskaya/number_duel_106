from rest_framework import viewsets, status, generics, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction as db_transaction
from .models import Room, Transaction
from .serializers import RoomSerializer, TransactionSerializer


class RoomViewSet(viewsets.ModelViewSet):
    """
    Oyun odaları API endpoint'i
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # OPEN ve FULL (oynanmakta olan) odaları listele
        if self.action == 'list':
            return Room.objects.filter(
                status__in=['OPEN', 'FULL']
            ).order_by('-created_at')
        return Room.objects.all()

    def perform_create(self, serializer):
        """
        Oda oluştururken bakiye kontrolü yap
        """
        user = self.request.user
        bet_amount = serializer.validated_data['bet_amount']
        
        # Bakiye kontrolü
        if user.balance < bet_amount:
            raise serializers.ValidationError({"error": "Bakiye yetersiz!"})
        
        # Oda oluştur
        serializer.save(creator=user)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """
        Odaya katılma - Sadece ikinci oyuncu için
        """
        room = self.get_object()
        user = request.user

        # Creator kendi odasına zaten girmiş durumda, tekrar join yapamaz
        if room.creator == user:
            return Response(
                {"error": "Bu odayı sen oluşturdun, zaten içindesin!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Oda zaten dolu mu?
        if room.status != 'OPEN':
            return Response(
                {"error": "Bu oda artık müsait değil!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Bakiye kontrolü
        if user.balance < room.bet_amount:
            return Response(
                {"error": "Bakiye yetersiz!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Atomic transaction ile güvenli güncelleme
        with db_transaction.atomic():
            room.player2 = user
            room.status = 'FULL'
            room.save()
        
        return Response({
            "status": "Oyun başlıyor...", 
            "room_id": room.id
        }, status=status.HTTP_200_OK)


class TransactionListView(generics.ListAPIView):
    """
    Kullanıcının hesap hareketleri
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class LeaderboardView(APIView):
    """
    Top 10 oyuncu (kazanma sayısına göre)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # En çok kazanan 10 oyuncu
        top_players = User.objects.filter(
            total_games__gt=0  # En az 1 oyun oynamış
        ).order_by('-total_wins', '-balance')[:10]
        
        leaderboard_data = []
        for idx, player in enumerate(top_players, 1):
            leaderboard_data.append({
                'rank': idx,
                'username': player.username,
                'balance': float(player.balance),
                'total_games': player.total_games,
                'total_wins': player.total_wins,
                'win_rate': player.win_rate
            })
        
        return Response(leaderboard_data)
