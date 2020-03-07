from celery import Celery
import os

# 读取django的配置
os.environ["DJANGO_SETTINGS_MODULE"] = "meiduo_mall.settings.dev"

# 实例化Celery对象
app = Celery('meiduo') # 起个名字叫meiduo

# 加载配置文件
app.config_from_object('celery_tasks.config')

# 加载可用任务
app.autodiscover_tasks(['celery_tasks.sms',])

