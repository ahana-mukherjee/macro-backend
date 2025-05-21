
# messages/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render

User = get_user_model()

class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(Q(user1=self.request.user) | Q(user2=self.request.user))

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chatroom_id = self.kwargs['chatroom_id']
        return Message.objects.filter(chatroom_id=chatroom_id)

class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chatroom_id = kwargs.get('chatroom_id')
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        content = request.data.get('content')
        if not content:
            return Response({"error": "Content cannot be empty"}, status=400)
        message = Message.objects.create(
            chatroom=chatroom,
            sender=request.user,
            content=content
        )
        return Response(MessageSerializer(message).data, status=201)
