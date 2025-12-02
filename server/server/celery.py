# encoding: utf-8
# @File  : celery.py
# @Author: Jimmy Chen
# @Desc : 
# @Date  :  2025/08/13

import os
from celery import Celery

# 设置 Django 的 settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

# 创建 Celery 实例
app = Celery('Madmin')

# 使用 Django 的 settings 模块中的配置
# Celery 会自动查找以 'CELERY_' 开头的配置变量
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的 Django app 中加载任务模块
app.autodiscover_tasks()


# 可选: 定义一个测试任务
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
