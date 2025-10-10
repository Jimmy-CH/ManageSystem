
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def get_date_range(period, start_date=None, end_date=None):
    """
    定义时间范围工具函数
    :param period:
    :param start_date:
    :param end_date:
    :return:
    """
    now = datetime.now()
    if period == 'this_week':
        start = now - timedelta(days=now.weekday())  # 周一
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    elif period == 'last_week':
        start = now - timedelta(days=now.weekday() + 7)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    elif period == 'this_month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start + relativedelta(months=1)).replace(day=1)
        end = next_month - timedelta(microseconds=1)
    elif period == 'last_month':
        start = (now.replace(day=1) - relativedelta(months=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(day=1) - timedelta(microseconds=1)
    elif period == 'this_year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'custom' and start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # 默认本月
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start + relativedelta(months=1)).replace(day=1)
        end = next_month - timedelta(microseconds=1)
    return start, end
