import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AgentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"message": "Connected to LLM Agent WebSocket"}))

    async def receive(self, text_data):
        """Receives messages from the frontend and simulates agent actions."""
        data = json.loads(text_data)
        user_message = data.get("message", "")

        thoughts = [
            "Thought: I need to fetch the schema...",
            "Action: Calling DBSchemaTool...",
            "Thought: Now I need to generate SQL...",
            "Action: Executing SQL query...",
            "Result: 250 sales last month"
        ]

        for thought in thoughts:
            await asyncio.sleep(2)
            await self.send(json.dumps({"message": thought}))

    async def disconnect(self, close_code):
        print("WebSocket Disconnected")
