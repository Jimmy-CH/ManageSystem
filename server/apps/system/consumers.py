
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ConfigConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 加入 "config_updates" 组
        await self.channel_layer.group_add("config_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("config_updates", self.channel_name)

    # 接收组广播消息
    async def config_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'config_update',
            'data': message
        }))


class MenuUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 加入菜单更新组
        await self.channel_layer.group_add("menu_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("menu_updates", self.channel_name)

    # 接收广播消息
    async def menu_changed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'menu.update',
            'action': event['action'],  # 'create', 'update', 'delete'
            'menu_id': event.get('menu_id'),
            'timestamp': event['timestamp'],
        }))
