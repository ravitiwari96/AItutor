from rest_framework import serializers
from .models import AIChat

class AIChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChat
        fields = ['id', 'message', 'ai_response', 'created_at']
        read_only_fields = ['id', 'ai_response', 'created_at']

class AIChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChat
        fields = ['message']
        
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        if len(value) > 2000:
            raise serializers.ValidationError("Message is too long. Maximum 2000 characters allowed.")
        return value.strip()