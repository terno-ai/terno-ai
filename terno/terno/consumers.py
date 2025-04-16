import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TernoWebsockerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f"user_{self.scope['user'].id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type", "chat")
        user_message = data.get("message", "")

        if message_type == "chat":
            thoughts = [
                "Thought: I need to fetch the schema...",
                "Action: Calling DBSchemaTool...",
                "Thought: Now I need to generate SQL...",
                "Action: Executing SQL query...",
                "Result: 250 sales last month"
            ]

            for thought in thoughts:
                await asyncio.sleep(2)
                await self.send(json.dumps({
                    "type": "chat",
                    "message": thought
                }))
