import datetime
import hashlib
import base64
import urllib.parse
from dateutil import parser
import pytz
from django.conf import settings


def generate_ticket(system_key: str, timestamp: str, channel_id: str) -> str:
    """
    根据 systemKey + timestamp + channelId 生成 ticket
    步骤：
      1. 拼接字符串: systemKey + timestamp + channelId
      2. MD5 (UTF-8)
      3. Base64 编码
      4. 转为字符串
      5. URL 编码
    """
    raw = system_key + timestamp + channel_id
    md5_hash = hashlib.md5(raw.encode('utf-8')).digest()
    b64_bytes = base64.b64encode(md5_hash)
    ticket_raw = b64_bytes.decode('ascii')
    ticket_encoded = urllib.parse.quote(ticket_raw, encoding='utf-8')
    return ticket_encoded


def timestamp_ms_to_datetime(ts_ms):
    """将毫秒级时间戳转为无时区的 naive datetime（USE_TZ=False 时使用）"""
    if not ts_ms:
        return None
    return datetime.datetime.fromtimestamp(ts_ms / 1000)


def mask_id_number(value: str) -> str:
    """
    对证件号码进行脱敏
    仅根据字符串长度对证件号码进行脱敏，不依赖证件类型。
    """
    if not value:
        return ""

    value = str(value).strip()
    n = len(value)

    if n <= 4:
        return "*" * n
    elif 5 <= n <= 7:
        return value[0] + "*" * (n - 2) + value[-1]
    elif 8 <= n <= 10:
        return value[:2] + "*" * (n - 4) + value[-2:]
    elif 11 <= n <= 17:
        return value[:2] + "*" * (n - 6) + value[-4:]
    else:  # n >= 18
        # 身份证，采用标准脱敏
        return value[:6] + "*" * (n - 10) + value[-4:]


def mask_phone_number(value: str) -> str:
    """对手机号进行脱敏"""
    if not value:
        return ""
    if len(value) == 11 and value.isdigit():
        return value[:3] + "****" + value[7:]
    # 非标准手机号也做通用脱敏
    if len(value) >= 7:
        return value[:3] + "****" + value[-4:]
    return "*" * len(value)


def parse_oa_time(value):
    """
    解析 OA 返回的时间字符串，如 "2025-11-18T00:00:00.000+08:00"
    支持：
      - None / 空字符串 → 返回 None
      - ISO 8601 带时区字符串 → 转为 aware datetime
    """
    if not value or not isinstance(value, str):
        return None

    try:
        dt = datetime.datetime.fromisoformat(value)
        # 如果没有时区，默认设为东八区（根据业务）
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
        return dt
    except (ValueError, TypeError) as e:
        print(f"时间解析失败: {value}, 错误: {e}")
        return None


def make_naive_datetime(dt_str):
    if not dt_str:
        return None
    # 解析为带时区的 datetime
    dt = parser.isoparse(dt_str)
    if dt.tzinfo is not None:
        # 转换为项目设置的 TIME_ZONE（如 'Asia/Shanghai'），然后去掉时区
        tz = pytz.timezone(settings.TIME_ZONE)
        dt = dt.astimezone(tz).replace(tzinfo=None)
    return dt
