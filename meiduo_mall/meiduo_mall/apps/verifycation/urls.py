from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$',views.ImageCodeView.as_view()),
    url(r'^sms_codes/(?P<mobile>1[345789]\d{9})/$',views.SmsCodeView.as_view()),
]
