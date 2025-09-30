# yourapp/management/commands/generate_fake_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random
from system.models import SystemConfig, Menu, StorageConfig  # 替换 yourapp 为你的实际 app 名称


fake = Faker('zh_CN')  # 使用中文假数据


class Command(BaseCommand):
    help = '生成系统配置、菜单、存储配置的假数据'

    def handle(self, *args, **options):
        self.stdout.write('开始生成假数据...')

        with transaction.atomic():
            self.create_system_configs()
            self.create_menus()
            self.create_storage_configs()

        self.stdout.write(
            self.style.SUCCESS('✅ 假数据生成完成！')
        )

    def create_system_configs(self):
        configs = [
            {"key": "site_title", "label": "网站标题", "type": "text", "group": "basic", "value": fake.sentence(nb_words=3)},
            {"key": "admin_email", "label": "管理员邮箱", "type": "text", "group": "basic", "value": fake.email()},
            {"key": "max_upload_size", "label": "最大上传大小(MB)", "type": "number", "group": "basic", "value": "100"},
            {"key": "enable_register", "label": "是否开放注册", "type": "boolean", "group": "auth", "value": "true"},
            {"key": "seo_description", "label": "SEO描述", "type": "textarea", "group": "seo", "value": fake.paragraph()},
            {"key": "logo_url", "label": "网站Logo", "type": "image", "group": "basic", "value": fake.image_url()},
        ]
        for conf in configs:
            SystemConfig.objects.get_or_create(
                key=conf["key"],
                defaults={
                    "value": conf["value"],
                    "label": conf["label"],
                    "type": conf["type"],
                    "group": conf["group"],
                    "remark": fake.sentence() if random.random() > 0.5 else None
                }
            )
        self.stdout.write('✅ SystemConfig 数据已生成')

    def create_menus(self):
        # 先清空（可选）
        Menu.objects.all().delete()

        # 根菜单
        dashboard = Menu.objects.create(title="仪表盘", icon="dashboard", path="/dashboard", component="Dashboard", order=1)
        user_manage = Menu.objects.create(title="用户管理", icon="user", path="/user", component="User", order=2)
        system = Menu.objects.create(title="系统设置", icon="setting", order=3)

        # 子菜单
        Menu.objects.create(title="角色管理", parent=user_manage, path="/role", component="Role", order=1)
        Menu.objects.create(title="权限管理", parent=user_manage, path="/permission", component="Permission", order=2)

        Menu.objects.create(title="菜单管理", parent=system, path="/menu", component="Menu", order=1)
        Menu.objects.create(title="参数配置", parent=system, path="/config", component="SystemConfig", order=2)
        Menu.objects.create(title="存储配置", parent=system, path="/storage", component="StorageConfig", order=3)

        self.stdout.write('✅ Menu 数据已生成（含树形结构）')

    def create_storage_configs(self):
        storages = [
            {
                "name": "本地存储",
                "type": "local",
                "is_default": True,
                "base_url": "http://127.0.0.1:8000/media/",
                "config": {"upload_path": "/uploads"}
            },
            {
                "name": "MinIO测试",
                "type": "minio",
                "is_default": False,
                "base_url": "https://minio.example.com",
                "config": {
                    "endpoint": "minio.example.com",
                    "access_key": fake.lexify(text="????????????????"),
                    "secret_key": fake.lexify(text="????????????????????????????????"),
                    "bucket": "my-bucket",
                    "secure": True
                }
            },
            {
                "name": "阿里云OSS",
                "type": "aliyun",
                "is_default": False,
                "base_url": "https://my-bucket.oss-cn-beijing.aliyuncs.com",
                "config": {
                    "access_key_id": fake.lexify(text="LTAI?????????????"),
                    "access_key_secret": fake.lexify(text="????????????????????????????????"),
                    "bucket_name": "my-bucket",
                    "region": "cn-beijing"
                }
            }
        ]
        for s in storages:
            StorageConfig.objects.get_or_create(
                name=s["name"],
                defaults={
                    "type": s["type"],
                    "is_default": s["is_default"],
                    "base_url": s["base_url"],
                    "config": s["config"]
                }
            )
        self.stdout.write('✅ StorageConfig 数据已生成')
