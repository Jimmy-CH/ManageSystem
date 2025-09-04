
import redis
from django.db import models
from django.utils import timezone
from utils.redis_client import cache
import logging

logger = logging.getLogger(__name__)


class DateIncrementingIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 20)
        kwargs.setdefault('unique', True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_length') == 20:
            kwargs.pop('max_length')
        if kwargs.get('unique') is True:
            kwargs.pop('unique')
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not add or value:
            return value

        current_date = timezone.now().strftime('%Y%m%d')
        key = f"pk_counter:{current_date}"

        try:
            counter = cache.incr(key)
            if counter == 1:
                cache.touch(key, timeout=3 * 24 * 3600)  # 3天过期

            counter_str = str(counter).zfill(4)
            if len(counter_str) > 4:
                raise OverflowError(f"Daily ID overflow: {counter}")

            value = current_date + counter_str
            setattr(model_instance, self.attname, value)
            return value

        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error(f"Redis 连接失败: {e}")
            raise RuntimeError("Redis 服务不可用，无法生成唯一 ID。")
        except redis.RedisError as e:
            logger.error(f"Redis 操作失败: {e}")
            raise RuntimeError("Redis 操作异常。")
        except Exception as e:
            logger.error(f"生成 ID 时发生未知错误: {e}")
            raise
