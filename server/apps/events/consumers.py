
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        # 每个用户一个专属组，格式：user_{id}
        self.user_group_name = f"user_{self.user.id}"

        # 加入用户组
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    # 接收前端发来的消息（可选，用于心跳或确认）
    async def receive(self, text_data):
        data = json.loads(text_data)
        # 可用于响应前端 ping 等操作
        await self.send(text_data=json.dumps({
            "type": "pong",
            "message": "Connection alive"
        }))

    # 接收后端推送的消息
    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message,
            'timestamp': event.get('timestamp', ''),
            'incident_id': event.get('incident_id'),
            'action': event.get('action'),  # created, responded, resolved
        }))
