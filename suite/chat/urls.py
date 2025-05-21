from django.urls import path
from .views import ChatRoomListView, MessageListView, SendMessageView

urlpatterns = [
    path('chatrooms/', ChatRoomListView.as_view(), name='chatroom-list'),
    path('chatrooms/<int:chatroom_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('chatrooms/<int:chatroom_id>/send/', SendMessageView.as_view(), name='send-message'),
]
