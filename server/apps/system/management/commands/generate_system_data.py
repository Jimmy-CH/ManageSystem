
from django.core.management.base import BaseCommand
from django.conf import settings
from faker import Faker

# 安全防护：禁止在生产环境运行
if not settings.DEBUG:
    raise RuntimeError("❌ 禁止在生产环境运行此命令！")

# 导入模型
from apps.system.models import SystemConfig, Menu, StorageConfig

fake = Faker('zh_CN')


class Command(BaseCommand):
    help = '生成系统配置、菜单、存储配置的测试数据'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='清空现有数据（谨慎使用）')

    def handle(self, *args, **options):
        clear = options['clear']

        if clear:
            self.stdout.write(self.style.WARNING("⚠️ 正在清空 system 表数据..."))
            StorageConfig.objects.all().delete()
            Menu.objects.all().delete()
            SystemConfig.objects.all().delete()

        self.stdout.write("开始生成系统测试数据...")

        # ========================
        # 1. 系统参数配置
        # ========================
        config_groups = ['basic', 'seo', 'mail', 'auth', 'sms', 'oss']
        config_items = [
            # basic
            ("site_name", "MyAdmin", "网站名称", "text", "basic", "网站标题"),
            ("site_logo", "/static/logo.png", "网站LOGO", "image", "basic", None),
            ("record_number", "京ICP备12345678号", "备案号", "text", "basic", None),
            # seo
            ("seo_title", "管理系统", "SEO标题", "text", "seo", None),
            ("seo_keywords", "admin,system", "关键词", "text", "seo", None),
            ("seo_description", "这是一个后台管理系统", "描述", "textarea", "seo", None),
            # mail
            ("smtp_host", "smtp.example.com", "SMTP主机", "text", "mail", None),
            ("smtp_port", 587, "SMTP端口", "number", "mail", None),
            ("smtp_user", "admin@example.com", "发件邮箱", "text", "mail", None),
            ("smtp_password", "******", "SMTP密码", "text", "mail", "敏感信息"),
            ("email_enabled", True, "启用邮件", "boolean", "mail", None),
            # auth
            ("login_captcha", True, "登录验证码", "boolean", "auth", None),
            ("max_login_attempts", 5, "最大登录尝试次数", "number", "auth", None),
        ]

        created_configs = 0
        for key, value, label, typ, group, remark in config_items:
            obj, created = SystemConfig.objects.get_or_create(
                key=key,
                defaults={
                    'value': str(value),
                    'label': label,
                    'type': typ,
                    'group': group,
                    'remark': remark,
                }
            )
            if created:
                created_configs += 1

        self.stdout.write(self.style.SUCCESS(f"✅ 系统配置: {created_configs} 项"))

        # ========================
        # 2. 菜单（树形结构）
        # ========================
        # 先创建顶级菜单
        top_menus = [
            ("系统管理", "system", "/system", "Layout", None, 1, True, None),
            ("内容管理", "content", "/content", "Layout", None, 2, True, None),
            ("用户中心", "user", "/user", "Layout", None, 3, True, None),
        ]

        menu_objects = {}
        for title, icon, path, component, parent_key, order, visible, perm in top_menus:
            menu = Menu.objects.create(
                title=title,
                icon=icon,
                path=path,
                component=component,
                parent=None,
                order=order,
                visible=visible,
                permission=perm
            )
            menu_objects[title] = menu

        # 创建子菜单
        sub_menus = [
            # 系统管理下
            ("用户管理", "user", "/system/user", "system/user/index", "系统管理", 1, True, "user:list"),
            ("角色管理", "role", "/system/role", "system/role/index", "系统管理", 2, True, "role:list"),
            ("菜单管理", "menu", "/system/menu", "system/menu/index", "系统管理", 3, True, "menu:list"),
            ("系统配置", "setting", "/system/config", "system/config/index", "系统管理", 4, True, "config:list"),
            ("存储配置", "storage", "/system/storage", "system/storage/index", "系统管理", 5, True, "storage:list"),
            # 内容管理下
            ("文章管理", "article", "/content/article", "content/article/index", "内容管理", 1, True, "article:list"),
            ("分类管理", "category", "/content/category", "content/category/index", "内容管理", 2, True, "category:list"),
            # 用户中心下
            ("个人资料", "profile", "/user/profile", "user/profile/index", "用户中心", 1, True, None),
            ("修改密码", "password", "/user/password", "user/password/index", "用户中心", 2, True, None),
        ]

        for title, icon, path, component, parent_title, order, visible, perm in sub_menus:
            parent = menu_objects.get(parent_title)
            if parent:
                Menu.objects.create(
                    title=title,
                    icon=icon,
                    path=path,
                    component=component,
                    parent=parent,
                    order=order,
                    visible=visible,
                    permission=perm
                )

        total_menus = Menu.objects.count()
        self.stdout.write(self.style.SUCCESS(f"✅ 菜单: {total_menus} 项"))

        # ========================
        # 3. 存储配置
        # ========================
        storage_configs = [
            {
                "name": "本地存储",
                "type": "local",
                "is_default": True,
                "config": {
                    "upload_path": "uploads/",
                    "max_size": 10 * 1024 * 1024,  # 10MB
                },
                "base_url": "http://localhost:8000/media/"
            },
            {
                "name": "MinIO 存储",
                "type": "minio",
                "is_default": False,
                "config": {
                    "endpoint": "http://minio.example.com:9000",
                    "access_key": fake.user_name(),
                    "secret_key": fake.password(),
                    "bucket": "my-bucket",
                    "secure": False
                },
                "base_url": "https://minio.example.com/my-bucket/"
            },
            {
                "name": "阿里云 OSS",
                "type": "aliyun",
                "is_default": False,
                "config": {
                    "access_key_id": fake.uuid4(),
                    "access_key_secret": fake.uuid4(),
                    "bucket_name": "my-oss-bucket",
                    "region": "cn-hangzhou",
                    "internal": False
                },
                "base_url": "https://my-oss-bucket.oss-cn-hangzhou.aliyuncs.com/"
            }
        ]

        created_storages = 0
        for cfg in storage_configs:
            obj, created = StorageConfig.objects.get_or_create(
                name=cfg["name"],
                defaults={
                    "type": cfg["type"],
                    "is_default": cfg["is_default"],
                    "config": cfg["config"],
                    "base_url": cfg["base_url"]
                }
            )
            if created:
                created_storages += 1

        self.stdout.write(self.style.SUCCESS(f"✅ 存储配置: {created_storages} 项"))

        self.stdout.write(self.style.SUCCESS("🎉 系统模块测试数据填充完成！"))

