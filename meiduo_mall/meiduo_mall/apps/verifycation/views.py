from django.shortcuts import render
from django.views import View
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import contants
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
import random
from meiduo_mall.libs.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms


# Create your views here.

class ImageCodeView(View):
    def get(self, request, uuid):
        # 接收
        # 验证
        # 处理

        # 1、生成图片文本，数据
        text, code, image = captcha.generate_captcha()

        # 2、保存文本，和用户对比
        redis_cli = get_redis_connection('image_code')
        redis_cli.setex(uuid, contants.IMAGE_CODE_EXPIRES, code)
        # 响应
        return HttpResponse(image, content_type='image/png')


class SmsCodeView(View):
    def get(self, request, mobile):
        # 1、接收 mobile可以直接取出用
        # 取出msg_code和uuid
        # print("11111",mobile)
        image_code = request.GET.get('image_code')
        image_code_id = request.GET.get('image_code_id')

        redis_sms = get_redis_connection('sms_code')
        # 判断是否频繁发送
        if redis_sms.get(mobile + '_flag') is not None:
            return HttpResponseForbidden("发送频繁")

        # 先判断是否全部为空
        if not all([image_code, image_code_id]):
            return JsonResponse({
                "err_msg": "某一项不能为空",
                "code": RETCODE.NODATAERR
            })
        # 取出redis里面的值，然后去判断
        redis_1 = get_redis_connection('image_code')
        redis_image_code = redis_1.get(image_code_id)
        # print("2222",mobile)
        if redis_image_code is None:
            return JsonResponse({
                "err_msg": "redis中不存在这样的值",
                "code": RETCODE.NODATAERR
            })
        # redis取出的值和传入image_code的值不相等
        if redis_image_code.decode('gbk').lower() != image_code.lower():
            return JsonResponse({
                "err_msg": "图形验证码和redis数值不匹配，请重新点击图片，生成新的验证码",
                "code": RETCODE.IMAGECODEERR
            })

        # 2、验证
        # 3、处理
        # 如果都相等就删除redis里面的值
        del redis_image_code
        # 生成随机6位数，并且保存在redis
        num = "%06d" % random.randint(0, 999999)  # 补齐6位数
        redis_sms_pipline = redis_sms.pipeline()
        redis_sms_pipline.setex(mobile, contants.SMS_CODE_EXPIRES, num)
        redis_sms_pipline.setex(mobile + '_flag', contants.PIPE_LINE_SMS, mobile)
        redis_sms_pipline.execute()  # pipeline()时一定要执行execute()
        print("短信验证码的值是:{}".format(num))
        # 发送短信
        # ccp = CCP()

        # # 按分钟计算
        # ccp.send_template_sms('18672687411', [num, contants.SMS_CODE_EXPIRES/60], 1)
        # send_sms.delay(mobile,num)   # 异步任务通过delay将任务加载到队列中，交给celery就行了

        # 4、响应
        return JsonResponse({
            "err_msg": "正确",
            "code": RETCODE.OK
        })
