
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view()),
    url(r"^usernames/(?P<user_name>[a-zA-Z0-9_-]{5,20})/count/$",views.UserNameCountView.as_view()),
    url(r"^mobiles/(?P<mobile>1[345789]\d{9})/count/$",views.MobileCountView.as_view()),
]
