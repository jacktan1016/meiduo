from django.shortcuts import render,redirect
from django.views import View
import re
from django.http import HttpResponseForbidden,JsonResponse
from .models import User
from django.contrib.auth import login,authenticate
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection

# Create your views here.
class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        # 1、接收

        # 用户名
        user_name = request.POST.get('user_name')
        # 密码
        pwd = request.POST.get('pwd')
        # 验证密码
        cpwd = request.POST.get('cpwd')
        # 手机号
        phone = request.POST.get('phone')
        # 图形验证码
        # pic_code = request.POST.get('pic_code')
        # 短信验证码
        msg_code = request.POST.get('msg_code')
        # 同意协议
        allow = request.POST.get('allow')

        # 2、验证
        # 首先判断不能全部为空
        if not all([user_name,pwd,cpwd,phone,msg_code,allow]):
            return HttpResponseForbidden("条件不能为空")

        # 判断用户是否符合格式
        if not re.match(r"^[a-zA-Z0-9_-]{5,20}$",user_name):
            return HttpResponseForbidden("用户名格式不对")

        # 判断用户是否重名
        if User.objects.filter(username=user_name).count() > 0:
            return HttpResponseForbidden("户与其他用户重名，请重新输入")

        # 判断密码是否一致
        if pwd!=cpwd:
            return HttpResponseForbidden("两次密码不一致，请重新输入")

        # 判断手机号格式是否正确
        if not re.match(r'^1[345789]\d{9}$',phone):
            return HttpResponseForbidden("手机号格式不正确")

        # 短信验证
        # 和redis的取值进行比较
        sms_redis = get_redis_connection('sms_code')
        sms_redis_code = sms_redis.get(phone)
        if sms_redis_code is None:
            return HttpResponseForbidden("验证码时间已经过期")
        if sms_redis_code.decode('gbk') != msg_code:
            return HttpResponseForbidden("对不起，验证码不正确")
        del  sms_redis_code

        # 3、处理


        # 注册用户
        user = User.objects.create_user(username=user_name,password=pwd,mobile=phone)

        # 保持状态
        login(request,user)

        # 4、响应
        return redirect('/')

class UserNameCountView(View):
    def get(self,request,user_name):
        # 判断是否存在重名
        print(user_name)
        count = User.objects.filter(username = user_name).count()
        print(count)
        # 返回值
        return JsonResponse({
            "count":count,
            "err_msg":"ok",
            "code":RETCODE.OK
            })

class MobileCountView(View):
    def get(self,request,mobile):
        # 接收
        # 验证
        # 处理:判断手机号是否存在
        count = User.objects.filter(mobile=mobile).count()
        # 响应
        return JsonResponse({
            "count":count,
            "err_msg":"ok",
            "code":RETCODE.OK
            })

# 登录
class LoginView(View):
    def get(self,request):
        return render(request,'login.html')


    def post(self,request):
        # 1、接收
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        # 2、验证
        # 是不是都为空
        if not all([username,pwd]):
            return HttpResponseForbidden('用户名或者密码错误')
        # 去判断是否和数据库的值是否相等
        user = authenticate(request,username=username,password = pwd)
        # 3、处理
        if user is None:
            return HttpResponseForbidden("用户名或者密码错误")
        else:
            # 4、响应
            # 保持状态
            login(request,user)
            return redirect('/')
