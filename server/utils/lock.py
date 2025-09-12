# encoding: utf-8
# @File  : lock.py
# @Author: Jimmy Chen
# @Desc : 
# @Date  :  2025/08/30

# utils/distributed_lock.py

import time
import uuid
import json
from typing import Optional


class RedisDistributedLock:
    def __init__(
        self,
        redis_cache,
        lock_key: str,
        expire_time: int = 120,
        max_retries: int = 10,
        retry_delay_min: float = 0.05,
        retry_delay_max: float = 0.5,
        timeout: Optional[int] = 60
    ):
        self.redis_cache = redis_cache
        self.lock_key = lock_key
        self.expire_time = expire_time
        self.max_retries = max_retries
        self.retry_delay_min = retry_delay_min
        self.retry_delay_max = retry_delay_max
        self.timeout = timeout

        self.lock_value = str(uuid.uuid4())
        self.locked = False
        self._acquired_at = None

    def acquire(self) -> bool:
        start_time = time.time()
        delay = self.retry_delay_min
        attempts = 0

        while attempts < self.max_retries:
            if self.timeout and (time.time() - start_time) >= self.timeout:
                return False

            result = self.redis_cache.set(
                self.lock_key,
                self.lock_value,
                expire=self.expire_time,
                nx=True  # only set if not exists
            )

            if result:
                self.locked = True
                self._acquired_at = time.time()
                return True

            time.sleep(delay)
            delay = min(delay * 2, self.retry_delay_max)
            attempts += 1

        return False

    def release(self):
        """释放锁：必须确保只删除自己持有的锁（原子性）"""
        if not self.locked:
            return False
        # 使用 Lua 脚本保证：GET 和 DEL 的原子性，避免误删
        lua_script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        try:
            serialized_value = json.dumps(self.lock_value)
            result = self.redis_cache._cache.eval(lua_script, 1, self.lock_key, serialized_value)
            if result == 1:
                self.locked = False
                return True
        except Exception as e:
            # 日志记录，但不要 raise，避免任务因锁释放失败而异常中断
            print(f"Failed to release lock {self.lock_key}: {e}")
        return False

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"Timeout acquiring lock: {self.lock_key}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

