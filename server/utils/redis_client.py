# encoding: utf-8
# @File  : redis_client.py
# @Author: Jimmy Chen
# @Desc : 
# @Date  :  2025/08/30


from django.core.cache import caches
from typing import Any, Optional, Union


class RedisClient:
    """
    封装 Redis 操作，便于在 Django 项目中使用不同 Redis DB。
    基于 Django 的 cache framework。
    """

    def __init__(self, cache_alias: str = 'default'):
        """
        初始化 Redis 客户端
        :param cache_alias: 对应 settings 中 CACHES 的 key，如 'default', 'session', 'temp'
        """
        try:
            self._cache = caches[cache_alias]
        except KeyError:
            raise ValueError(f"Redis cache alias '{cache_alias}' not found in settings.CACHES")

    def get(self, key: str) -> Any:
        """
        获取缓存值
        :param key: 键
        :return: 值（自动反序列化）
        """
        return self._cache.get(key)

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        设置缓存
        :param key: 键
        :param value: 值（支持任意 Python 对象）
        :param timeout: 过期时间（秒），None 表示永不过期
        :return: 是否成功
        """
        return self._cache.set(key, value, timeout)

    def delete(self, key: str) -> bool:
        """
        删除缓存
        :param key: 键
        :return: 是否成功
        """
        return self._cache.delete(key) > 0

    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        :param key: 键
        :return: 是否存在
        """
        return self._cache.get(key) is not None

    def ttl(self, key: str) -> Union[int, None]:
        """
        获取键的剩余生存时间（秒）
        注意：Django cache 不直接支持 TTL，需通过 Redis 原生客户端获取
        如果需要精确 TTL，建议引入 redis-py
        """
        # 警告：Django 缓存后端不提供 TTL 接口，这里返回 None 或使用原生连接
        # 如需 TTL，可扩展使用 redis-py 直接连接
        return None

    def incr(self, key: str, delta: int = 1) -> int:
        """
        自增（用于计数器）
        :param key: 键
        :param delta: 步长
        :return: 新值
        """
        return self._cache.incr(key, delta)

    def decr(self, key: str, delta: int = 1) -> int:
        """
        自减
        :param key: 键
        :param delta: 步长
        :return: 新值
        """
        return self._cache.decr(key, delta)

    def touch(self, key: str, timeout: Optional[int] = None) -> bool:
        """
        更新键的过期时间
        :param key: 键
        :param timeout: 新的过期时间（秒）
        :return: 是否成功
        """
        return self._cache.touch(key, timeout)

    def clear(self):
        """
        清空当前 cache（慎用）
        """
        self._cache.clear()


# 快捷实例（可选）
cache = RedisClient('default')      # 默认缓存
session_cache = RedisClient('session')  # 会话缓存
temp_cache = RedisClient('temp')    # 临时数据
