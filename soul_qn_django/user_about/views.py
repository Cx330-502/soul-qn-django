import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from Qn.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import user_about.extra_codes.captcha as captchaclass
import json


# Create your views here.
# 发送验证码的视图函数，由前端检查验证码是否正确 （验证码目前不支持QQ邮箱）
@csrf_exempt
def captcha(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    receiver_email = body.get("email")
    try:
        validate_email(receiver_email)
    except ValidationError:
        return JsonResponse({'errno': 1002, 'errmsg': '邮箱不符合规范'})
    verification = captchaclass.SendEmail(data=captchaclass.data, receiver=receiver_email).send_email()
    return JsonResponse({'errno': 0, 'errmsg': '验证码发送成功', 'verification': verification})


# 注册，email和username不能重复
@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    username = body.get("username")
    password = body.get("password")
    email = body.get("email")
    if not re.match(r"^[a-zA-Z0-9_-]{4,16}$", username):
        return JsonResponse({'errno': 1002, 'errmsg': '用户名不符合规范'})
    if not re.match(r"^[a-zA-Z0-9_-]{6,16}$", password):
        return JsonResponse({'errno': 1003, 'errmsg': '密码不符合规范'})
    if User.objects.filter(username=username).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '用户名已存在'})
    if User.objects.filter(email=email).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '邮箱已存在'})
    user = User(username=username, password=password, email=email)
    user.save()
    return JsonResponse({'errno': 0, 'errmsg': '注册成功'})


# 登录，用户名和密码正确则返回token
@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    username = body.get("username")
    password = body.get("password")
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    elif User.objects.filter(email=username).exists():
        user = User.objects.get(email=username)
    else:
        return JsonResponse({'errno': 1001, 'errmsg': '用户名或邮箱不存在'})
    if user.password == password:
        token = user.create_token(3600*24)
        return JsonResponse({'errno': 0, 'errmsg': '登录成功', 'token': token})
    return JsonResponse({'errno': 1002, 'errmsg': '密码错误'})


# 一个token测试的视图函数，前端传入token，后端验证token是否正确
@csrf_exempt
def test_login(request):
    body = json.loads(request.body)
    token = body.get("token")
    print(token)
    user = auth_token(token)
    if user:
        return JsonResponse({'errno': 0, 'errmsg': '登录成功'})
    return JsonResponse({'errno': 1001, 'errmsg': '登录失败'})
