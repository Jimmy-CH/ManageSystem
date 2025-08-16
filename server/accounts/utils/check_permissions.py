# rbac/utils.py
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from accounts.models import UserRole, Role, CustomPermission

# 缓存配置
PERMISSION_CACHE_TIMEOUT = getattr(settings, 'PERMISSION_CACHE_TIMEOUT', 60 * 15)  # 15分钟
PERMISSION_CACHE_PREFIX = 'user_perms_'


def _get_user_permission_cache_key(user_id):
    """生成用户权限缓存的键"""
    return f"{PERMISSION_CACHE_PREFIX}{user_id}"


def _get_user_permissions_from_db(user: User) -> set:
    """
    从数据库查询用户拥有的所有活跃自定义权限的 codename 集合。
    这是缓存未命中时的后备查询。
    """
    if not user.is_authenticated:
        return set()

    # 超级用户拥有所有活跃权限
    if user.is_superuser:
        return set(
            CustomPermission.objects
            .filter(is_active=True)
            .values_list('codename', flat=True)
        )

    # 查询用户拥有的、未过期的角色所关联的活跃权限
    active_perms = CustomPermission.objects.filter(
        is_active=True,
        roles__user_roles__user=user,
        roles__user_roles__expires_at__isnull=True # 未过期
    ).values_list('codename', flat=True)

    return set(active_perms)


def get_user_permissions(user: User, use_cache=True) -> set:
    """
    获取用户拥有的所有自定义权限的 codename 集合。
    支持缓存。
    """
    if not user.is_authenticated:
        return set()

    if not use_cache:
        return _get_user_permissions_from_db(user)

    # 使用缓存
    cache_key = _get_user_permission_cache_key(user.id)
    cached_perms = cache.get(cache_key)

    if cached_perms is None:
        # 缓存未命中，查询数据库并设置缓存
        perms = _get_user_permissions_from_db(user)
        cache.set(cache_key, perms, timeout=PERMISSION_CACHE_TIMEOUT)
        return perms

    return cached_perms


def clear_user_permissions_cache(user: User):
    """
    清除指定用户的权限缓存。
    当用户的权限或角色发生变化时调用。
    """
    cache_key = _get_user_permission_cache_key(user.id)
    cache.delete(cache_key)


def has_permission(user: User, codename: str, use_cache=True) -> bool:
    """
    检查用户是否拥有指定的自定义权限。

    Args:
        user (User): Django 用户对象。
        codename (str): 权限的 codename，如 'view_dashboard'。
        use_cache (bool): 是否使用缓存。默认为 True。

    Returns:
        bool: 用户是否拥有该权限。
    """
    if not user or not user.is_authenticated:
        return False

    # 1. 超级用户拥有所有权限
    if user.is_superuser:
        return True

    # 2. 检查用户是否拥有指定的权限
    user_perms = get_user_permissions(user, use_cache=use_cache)
    return codename in user_perms


def has_any_permission(user: User, codenames: list, use_cache=True) -> bool:
    """
    检查用户是否拥有列表中任意一个权限。
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    user_perms = get_user_permissions(user, use_cache=use_cache)
    return bool(set(codenames) & user_perms)


def has_all_permissions(user: User, codenames: list, use_cache=True) -> bool:
    """
    检查用户是否拥有列表中所有权限。
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    user_perms = get_user_permissions(user, use_cache=use_cache)
    return set(codenames).issubset(user_perms)


# 更高级的检查：结合对象状态
def has_object_permission(user: User, codename: str, obj, use_cache=True) -> bool:
    """
    检查用户是否对特定对象拥有指定权限。
    这需要业务逻辑的支持。例如，检查用户是否是对象的作者。

    Args:
        user (User): 用户
        codename (str): 权限码
        obj: 要检查权限的Django模型对象
        use_cache (bool): 是否使用缓存

    Returns:
        bool: 是否有权限
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    # 先检查基础权限
    if not has_permission(user, codename, use_cache=use_cache):
        return False

    # 如果有基础权限，再检查对象级规则
    # 示例：只有文章作者才能编辑自己的文章（即使有 'edit_article' 权限）
    if codename == 'edit_article' and hasattr(obj, 'author'):
        return obj.author == user

    # 示例：只有在订单状态为 'pending' 时才能取消
    if codename == 'cancel_order' and hasattr(obj, 'status'):
        return obj.status == 'pending'

    # 默认：如果拥有基础权限，则允许
    return True
