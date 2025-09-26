from django.core.management.base import BaseCommand
from scripts.generate_user_data import main


class Command(BaseCommand):
    help = '生成假数据：权限、角色、用户'

    def handle(self, *args, **kwargs):
        main()
        self.stdout.write(self.style.SUCCESS('🎉 假数据生成完成！'))

