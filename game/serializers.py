from rest_framework import serializers
from .models import Room, GlobalSettings, Transaction


class RoomSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='creator.username')
    player_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'bet_amount', 'creator_name', 'player_count', 'status', 'created_at']
        read_only_fields = ['creator_name', 'player_count', 'status', 'created_at']

    def get_player_count(self, obj):
        count = 1
        if obj.player2:
            count += 1
        return count

    def validate_bet_amount(self, value):
        config = GlobalSettings.objects.get_or_create(pk=1)[0]
        
        if value < config.min_bet or value > config.max_bet:
            raise serializers.ValidationError(
                f"Bahis {config.min_bet} ile {config.max_bet} arasında olmalı!"
            )
        if 'request' in self.context:
            user = self.context['request'].user
            if user.balance < value:
                raise serializers.ValidationError("Bakiye yetersiz!")
        
        return value


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'description', 'created_at']