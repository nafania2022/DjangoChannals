import json
from channels.exceptions import DenyConnection
from django.shortcuts import redirect

from .models import Chat, User, Message
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    user_count = 0

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        try:
            await self.create_chat(self.room_name, self.scope["user"])
        except Exception as e:
            print('канал уже создан')
        self.chat = await self.get_chat(self.room_name)
        self.friends_creator_chat = await self.get_friend_data(self.chat.chat_creator)
        self.friends = await self.get_friend_data(self.scope['user'])
        self.no_friends = await self.get_user_no_friends(self.friends)
        ChatConsumer.user_count += 1
        print(ChatConsumer.user_count)
        print(self.scope['user'])
        print(self.friends_creator_chat)
        print(str(self.scope['user'])  in self.friends_creator_chat)
        print(self.scope['user'] != self.chat.chat_creator)
        if ChatConsumer.user_count > 2 or (str(self.scope['user']) not in self.friends_creator_chat and self.scope['user'] != self.chat.chat_creator):
            # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            await self.accept()
            await self.send(text_data=json.dumps({"type": "disconnect"}))
            # await self.close('disconnect')
        else:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            self.chat_data = await self.get_chat_data(self.chat.pk)
            for data in self.chat_data:
                await self.send(text_data=json.dumps({
                    "type": "chat_message",
                    "message": data['message'],
                    "username": data['user_name'],
                    "date": data['date'],
                }))
            await self.send(text_data=json.dumps({
                "type": "response",
                "no_friends": self.no_friends,
                "friends": self.friends
            }))

        # Join room group

    async def disconnect(self, close_code):
        # Leave room group
        ChatConsumer.user_count -= 1
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        if text_data_json['type'] == 'chat_message':
            message = text_data_json["message"]
            user = text_data_json["user"]
            await self.create_message(self.chat, message, self.scope['user'])
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": message, "user": user}
            )
        elif text_data_json['type'] == 'form_data':
            print(text_data_json)
            await self.add_friend(text_data_json['data'])

    # Receive message from room group
    async def chat_message(self, event):
        print(event)
        message = event["message"]
        user_auth = event["user"]
        # Send message to WebSocket        # Send message to WebSocket
        await self.send(text_data=json.dumps({
                                            "type": "chat_message",
                                            "message": message,
                                            "username": user_auth,
                                            "date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}))

    @database_sync_to_async
    def create_message(self, chat_name, message, username):
        chat = Message.objects.create(chat_name=chat_name, message=message, user_name=username)
        return chat

    @database_sync_to_async
    def get_chat_data(self, chat_name):
        chat_data = []
        for chat_filter in Message.objects.filter(chat_name=chat_name):
            chat_data.append({'user_name': chat_filter.user_name.username,
                              'chat_name': chat_filter.chat_name.chat_name,
                              'message': chat_filter.message,
                              'date': chat_filter.date.strftime("%Y-%m-%d %H:%M:%S")
                              })
        return chat_data

    @database_sync_to_async
    def add_friend(self, user_name):
        user = User.objects.get(username=user_name)
        friend = User.objects.get(username=self.scope['user']).friends.add(user)
        return friend

    @database_sync_to_async
    def get_friend_data(self, user_name):
        friends = []
        user = User.objects.get(username=user_name)
        for friend in user.friends.all().values():
            # print(friend)
            friends.append(friend['username'])
        return friends

    @database_sync_to_async
    def get_user_no_friends(self, friends):
        users = User.objects.exclude(username=self.scope['user'])
        list_no_friends = []
        for user in users:
            if user.username not in friends:
                list_no_friends.append(user.username)
        return list_no_friends

    @database_sync_to_async
    def create_chat(self, chat_name, user_name):
        chat = Chat.objects.create(chat_name=chat_name, chat_creator=user_name)
        return chat

    @database_sync_to_async
    def get_chat(self, chat_name):
        chat = Chat.objects.filter(chat_name=chat_name)
        for chat in chat:
            print(chat.chat_name)
            print(chat.chat_creator)
        return chat
