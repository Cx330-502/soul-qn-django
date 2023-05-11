from django.urls import path
from .views import *

urlpatterns = [
    path('register/captcha', captcha),
    path('register', register),
    path('login', login),
    path('test_login', test_login),
]
