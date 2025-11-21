
from django.core.management.base import BaseCommand
from apps.cmdb.models import Asset


class Command(BaseCommand):
    help = '生成测试资产数据（含加密密码）'

    def handle(self, *args, **options):
        assets_data = [
            {
                "name": "Web Server 02",
                "ip": "10.130.16.135",
                "port": 22,
                "username": "testadmin",
                "password": "U7H8U2Bfmrzd",
                "os_type": "Linux"
            },
            # {
            #     "name": "DB Server 01",
            #     "ip": "192.168.1.11",
            #     "port": 22,
            #     "username": "admin",
            #     "password": "dbpass456@",
            #     "os_type": "Ubuntu"
            # },
            # {
            #     "name": "Jump Host",
            #     "ip": "192.168.1.12",
            #     "port": 2222,
            #     "username": "deploy",
            #     "password": "jump789#",
            #     "os_type": "CentOS"
            # },
        ]

        created_count = 0
        for data in assets_data:
            obj, created = Asset.objects.get_or_create(
                ip=data["ip"],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'成功创建资产: {obj.name} ({obj.ip})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'资产已存在，跳过: {data["ip"]}')
                )

        self.stdout.write(
            self.style.NOTICE(f'共创建 {created_count} 条资产记录。')
        )


