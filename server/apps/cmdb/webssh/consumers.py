
import asyncio
import threading
import queue
import paramiko
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from apps.cmdb.models import Asset


class WebSSHConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.asset = None
        self.ssh = None
        self.chan = None
        self.data_queue = None
        self.read_thread = None
        self._stop_event = threading.Event()

    async def connect(self):
        asset_id = self.scope['url_route']['kwargs'].get('asset_id')
        if not str(asset_id).isdigit():
            await self.close(code=4000)
            return

        try:
            self.asset = await sync_to_async(Asset.objects.get)(id=int(asset_id))
        except ObjectDoesNotExist:
            await self.send(text_data="❌ 资产不存在")
            await self.close()
            return

        await self.accept()
        await self.send(text_data="⏳ 正在连接...\n")

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self._connect_ssh)
            await self.send(text_data="✅ SSH 连接成功！\n")

            # 启动读取线程
            self.data_queue = queue.Queue()
            self._stop_event.clear()
            self.read_thread = threading.Thread(target=self._read_ssh_output, daemon=True)
            self.read_thread.start()

            # 启动异步推送任务
            asyncio.create_task(self._send_ssh_output())
        except Exception as e:
            error_msg = f"❌ 连接失败: {str(e)}"
            print(f"[SSH ERROR] Asset {asset_id}: {e}")
            await self.send(text_data=error_msg)
            await self.close()

    def _connect_ssh(self):
        """在子线程中同步连接 SSH"""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=self.asset.ip,
            port=self.asset.port,
            username=self.asset.username,
            password=self.asset.password,
            timeout=10,
            look_for_keys=False,
            allow_agent=False,
        )
        self.chan = self.ssh.invoke_shell(term='xterm', width=120, height=30)
        self.chan.settimeout(30.0)

    def _read_ssh_output(self):
        """持续读取 SSH 输出"""
        while not self._stop_event.is_set():
            try:
                if not self.chan or self.chan.closed:
                    break

                # 阻塞读取，但 Paramiko 默认是阻塞的
                data = self.chan.recv(1024)

                if data == b'':  # EOF，连接被对端关闭
                    print("[SSH] Received EOF, remote closed connection")
                    break

                self.data_queue.put(data)

            except Exception as e:
                # 打印完整异常信息！
                import traceback
                print(f"[READ ERROR] Exception in SSH read thread: {e}")
                print(traceback.format_exc())
                break

        self._stop_event.set()

    async def _send_ssh_output(self):
        """从队列取数据并发送到 WebSocket"""
        while not self._stop_event.is_set():
            try:
                if not self.data_queue.empty():
                    data = self.data_queue.get_nowait()
                    await self.send(text_data=data.decode('utf-8', errors='ignore'))
                else:
                    await asyncio.sleep(0.01)
            except Exception as e:
                print(f"[SEND ERROR] {e}")
                break
        # 主动关闭连接
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        if self.chan and not self.chan.closed:
            try:
                self.chan.send(text_data.encode('utf-8'))
            except Exception as e:
                print(f"[SEND INPUT ERROR] {e}")

    async def disconnect(self, code):
        self._stop_event.set()
        if self.chan:
            try:
                self.chan.close()
            except:
                pass
        if self.ssh:
            try:
                self.ssh.close()
            except:
                pass
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1)


