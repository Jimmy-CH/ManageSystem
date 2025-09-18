
from django.core.management.base import BaseCommand, CommandError
from scripts.clear_fake_data import main


class Command(BaseCommand):
    help = '清空假数据：权限、角色、用户（默认保留超级用户）'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='清空所有数据（包括超级用户）')
        parser.add_argument('--no-perm', action='store_true', help='不清空权限')
        parser.add_argument('--no-role', action='store_true', help='不清空角色')
        parser.add_argument('--no-user', action='store_true', help='不清空用户')

    def handle(self, *args, **options):
        clear_perms = not options['no_perm']
        clear_roles_flag = not options['no_role']
        clear_users_flag = not options['no_user']
        keep_superusers = not options['all']

        if not any([clear_perms, clear_roles_flag, clear_users_flag]):
            self.stdout.write(self.style.WARNING("⚠️  未选择任何清空项，无操作"))
            return

        main(
            clear_perms=clear_perms,
            clear_roles_flag=clear_roles_flag,
            clear_users_flag=clear_users_flag,
            keep_superusers=keep_superusers
        )

        self.stdout.write(self.style.SUCCESS('✅ 数据清空完成！'))
