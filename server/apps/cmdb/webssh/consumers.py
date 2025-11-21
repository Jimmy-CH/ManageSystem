
import asyncio
import paramiko
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.cmdb.models import Asset


class WebSSHConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.asset_id = self.scope['url_route']['kwargs']['asset_id']
        await self.accept()


        try:
            asset = await Asset.objects.aget(id=self.asset_id)
        except Asset.DoesNotExist:
            await self.send(text_data="资产不存在")
            await self.close()
            return

        # 建立 SSH 连接
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(
                hostname=asset.ip,
                port=asset.port,
                username=asset.username,
                password=asset.password,
                timeout=5
            )
            self.chan = self.ssh.invoke_shell(term='xterm', width=120, height=30)
            await self.send(text_data="SSH 连接成功！\n")
            asyncio.create_task(self._read_ssh_output())
        except Exception as e:
            await self.send(text_data=f"连接失败: {str(e)}")
            await self.close()

    async def disconnect(self, code):
        if hasattr(self, 'chan'):
            self.chan.close()
        if hasattr(self, 'ssh'):
            self.ssh.close()

    async def receive(self, text_data):
        if hasattr(self, 'chan') and self.chan:
            self.chan.send(text_data)

    async def _read_ssh_output(self):
        while True:
            if self.chan.recv_ready():
                data = self.chan.recv(1024)
                await self.send(text_data=data.decode('utf-8', errors='ignore'))
            else:
                await asyncio.sleep(0.05)


