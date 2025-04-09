import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TernoWebsockerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

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

        elif message_type == "notification":
            await self.send(json.dumps({
                "type": "notification",
                "message": "Notification received",
                "data": data.get("data")
            }))

    async def disconnect(self, close_code):
        print("WebSocket Disconnected")
