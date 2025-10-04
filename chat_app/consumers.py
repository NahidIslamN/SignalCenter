import json
import base64
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import *



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.room_name = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.room_name}"

        if await self.check_able_connect_or_not():
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message", "")
        files_data = data.get("files", [])  # [{"title":"img.png","file_base64":"data:image/png;base64,...."}]

        # Save message + files
        message_obj = await self.save_message_to_database(message_text, files_data)
        files_urls = await self.get_message_files(message_obj)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_text,
                "username": getattr(self.user, "username", "Anonymous"),
                "files": files_urls
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
            "files": event.get("files", [])
        }))

    # ---------------- DB helpers ----------------

    @database_sync_to_async
    def check_able_connect_or_not(self):
        chat = Chat.objects.get(id=self.room_name)
        return self.user in chat.participants.all()

    @database_sync_to_async
    def get_message_files(self, message_obj):
        return [f.file.url for f in message_obj.files.all()]

    @database_sync_to_async
    def save_message_to_database(self, message_text, files):
        chat = Chat.objects.get(id=self.room_name)
        msg_obj = Message.objects.create(chat=chat, sender=self.user, text=message_text)

        for f in files:
            title = f.get("title", "")
            file_base64 = f.get("file_base64")
            if file_base64:
                format, imgstr = file_base64.split(';base64,')
                ext = format.split('/')[-1]  # e.g., png, jpg
                data = ContentFile(base64.b64decode(imgstr), name=f"{title}.{ext}")
                file_obj = MessageFiles.objects.create(title=title, file=data)
                msg_obj.files.add(file_obj)

        return msg_obj





class Sent_Reaction_ON_Message(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.room_name = self.scope['url_route']['kwargs']['message_id']
        self.room_group_name = f"react_to_{self.room_name}"

        if await self.check_able_connect_or_not():
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        emuji = data.get("message", "")

        await self.save_reaction_into_message(emuji)


        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "emoji_sender",
                "message": emuji,
                "username": getattr(self.user, "username"),
             
            }
        )

    async def emoji_sender(self, event):
        await self.send(text_data=json.dumps({
            "emuji": event["message"],
            "username": event["username"],
            "message_id":self.room_name
            
        }))

    # ---------------- DB helpers ----------------

    @database_sync_to_async
    def check_able_connect_or_not(self):
        message = Message.objects.get(id=self.room_name)
        return self.user in message.chat.participants.all()

    @database_sync_to_async
    def save_reaction_into_message(self, emuji):
        try:
            message = Message.objects.get(id = self.room_name)
            if MessageReaction.objects.filter(user = self.user, emoji = emuji).exists():
                reaction = MessageReaction.objects.filter(user = self.user, emoji = emuji).first()
            else:
                reaction = MessageReaction.objects.create(
                    user=self.user,
                    emoji = emuji
                )
            message.reactions.add(reaction)
            message.save()
            return emuji
        except:
            return "message not found"


