# messages/services.py
from .models import ChatRoom
from django.db.models import Q

def get_or_create_room(user1, user2):
    room = ChatRoom.objects.filter(
        Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
    ).first()

    if not room:
        room = ChatRoom.objects.create(user1=user1, user2=user2)

    return room