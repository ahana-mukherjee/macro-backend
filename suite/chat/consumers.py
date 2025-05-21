# messages/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"WebSocket connection attempt: {self.scope['url_route']['kwargs']}")
        print(f"User: {self.scope['user']}")
        self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        self.room_group_name = f"chat_{self.chatroom_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(f"Received message: {text_data}")
        data = json.loads(text_data)
        print(f"Sender ID: {data.get('sender_id')}")
        print(f"Chatroom ID: {data.get('chatroom_id')}")
        message = data["message"]
        sender_id = data["sender_id"]

        # Save to DB
        await self.save_message(sender_id, message)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_id": sender_id,
            }
        )
        # Broadcast typing status
        if "typing" in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_typing",
                    "sender_id": sender_id,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            "sender_id": event["sender_id"],
            "typing": True,
        }))
    # New method to mark message as read
    async def mark_message_as_read(self, message_id):
        await self.mark_as_read(message_id)
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         "type": "mark_message_as_read",
        #         "message_id": message_id,
        #     }
        # )
    @database_sync_to_async
    def save_message(self, sender_id, message):
        sender = User.objects.get(id=sender_id)
        chatroom = ChatRoom.objects.get(id=self.chatroom_id)
        return Message.objects.create(chatroom=chatroom, sender=sender, content=message)

    @database_sync_to_async
    def mark_as_read(self, message_id):
        message = Message.objects.get(id=message_id)
        message.is_read = True
        message.save()