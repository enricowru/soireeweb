import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()

class EventBookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['chat_id']

        # self.booking_id = self.scope['url_route']['kwargs']['id']
        self.group_name = f"booking_{self.booking_id}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive a message from WebSocket, parse it and broadcast accordingly.
        Expect data like:
        {
            "type": "chat_message",
            "message": "Hello",
            "sender_id": 1
        }
        """
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "chat_message":
            message_text = data.get("message")
            sender_id = data.get("sender_id")

            # Optional: Validate sender is in chat participants, etc.

            # Save the message in the DB
            try:
                chat = await self.get_chat()
                sender = await self.get_user(sender_id)

                message = await self.create_message(chat, sender, message_text)

                # Prepare payload to broadcast
                payload = {
                    "type": "chat_message",  # event type for consumers
                    "message": {
                        "id": message.id,
                        "chat_id": chat.id,
                        "sender": {"id": sender.id, "username": sender.username},
                        "content": message.content,
                        "timestamp": message.created_at.isoformat(),
                    },
                }

                # Broadcast to group
                await self.channel_layer.group_send(self.group_name, payload)

            except Exception as e:
                # You can add error handling/logging here
                await self.send(text_data=json.dumps({"error": str(e)}))

        elif event_type == "booking_message":
            # Handle booking related messages if any
            pass

    async def chat_message(self, event):
        # Send chat message to WebSocket client
        await self.send(text_data=json.dumps(event["message"]))

    async def booking_message(self, event):
        # Send booking message to WebSocket client
        await self.send(text_data=json.dumps(event["data"]))

    # Helper async DB methods (using sync_to_async for ORM calls)
    from asgiref.sync import sync_to_async

    @sync_to_async
    def get_chat(self):
        return Chat.objects.get(id=self.booking_id)

    @sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @sync_to_async
    def create_message(self, chat, sender, content):
        return Message.objects.create(chat=chat, sender=sender, content=content, is_read=False)
