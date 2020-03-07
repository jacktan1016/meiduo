import re

from django.contrib.auth.backends import ModelBackend
from users.models import User

class MeiDuoModelBackend(ModelBackend):
    # authenticate 这个方法返回值是user对象或者None
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断用户是用用户名登录了，还是电话号码去登录,先用用户名去判断，然后再用电话号码登录
        try:
            user = User.objects.get(username=username)
        except:
            try:
                user = User.objects.get(mobile=username)
            except:
                return None
        # 判断密码,check_password正确的话就返回True
        if user.check_password(password):
            return user
        else:
            return None

