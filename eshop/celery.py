import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings')

celery = Celery('eshop')    # 创建一个celery实例，并起名eshop

# 指定celery从哪里可以找到配置变量， 设置前缀为CELERY
celery.config_from_object('django.conf:settings', namespace='CELERY')

celery.autodiscover_tasks()