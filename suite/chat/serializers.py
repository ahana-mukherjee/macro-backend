# messages/serializers.py
from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class ChatRoomSerializer(serializers.ModelSerializer):
    user1 = UserSimpleSerializer(read_only=True)
    user2 = UserSimpleSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'user1', 'user2', 'created_at', 'last_message']

    def get_last_message(self, obj):
        last = obj.messages.order_by('-timestamp').first()
        if last:
            return MessageSerializer(last).data
        return None

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chatroom', 'sender', 'content', 'timestamp', 'is_read']
        read_only_fields = ['timestamp', 'sender', 'is_read']