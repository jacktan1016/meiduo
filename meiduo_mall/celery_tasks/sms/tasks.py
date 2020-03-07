from celery_tasks.main import app
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import contants

# bind=true表示将当前任务当作对象传入到函数， retry_backoff=3表示失败后相隔多少时间重试
@app.task(bind=True, name='send_sms', retry_backoff=3)
def send_sms(self,mobile,num):
    # 实例化第三方模块
    ccp = CCP()
    # 发送短信,记得加个self!,send_ret表示不等于0就重试
    send_ret = ccp.send_template_sms(
        mobile,[num,contants.SMS_CODE_EXPIRES],1) # 直接写5分钟
    print("num的值已发送，发送的值是:".format(num))
    if send_ret !=0:
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)
    # return send_ret


