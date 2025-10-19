import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .chat_memory import push  # << novo

class PresencaConsumer(AsyncWebsocketConsumer):
    room_group_name = 'chat_ao_vivo_global'

    async def connect(self):
        print(">>> NOVA CONEXÃO AO CHAT GLOBAL <<<")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("--- CONEXÃO FECHADA DO CHAT GLOBAL ---")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        print(f"!!! MENSAGEM RECEBIDA NO CHAT GLOBAL: {text_data} !!!")

        # Aceita JSON {"type":"chat_message","user_name":"...","message":"..."} ou texto puro
        try:
            data = json.loads(text_data)
            user_name = data.get("user_name", "Anônimo")
            message = data.get("message", "")
        except Exception:
            user_name = "Anônimo"
            message = text_data

        # Guarda no histórico em memória
        push(user_name, message)

        # Reenvia padronizado como JSON (o app já entende esse formato)
        payload = json.dumps({
            "type": "chat_message",
            "user_name": user_name,
            "message": message
        })

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "broadcast_message", "message": payload}
        )

    async def broadcast_message(self, event):
        await self.send(text_data=event["message"])
