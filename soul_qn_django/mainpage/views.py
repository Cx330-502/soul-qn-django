from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from Qn.models import *
import json


# Create your views here.


def hello(request):
    return JsonResponse({'message': 'Hello, world!'})


@login_required
def listqn_views(request):
    user = request.user
    userid = user.id
    # 读当前用户创建的问卷
    user_questionnaire = User_create_Questionnaire.objects.filter(user_id=userid)
    context = {'questionnaires': user_questionnaire}
    return render(request, 'listqn.html', context)


# 生成链接
def generate_link(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_id = body.get("qn_id")
    if not qn_id:
        return JsonResponse({'errno': 1003, 'errmsg': '问卷id不能为空'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if qn.link is None or qn.link == "":
        qn.link = qn.generate_link()
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'link': qn.link})


# 生成二维码
def generate_qrcode(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_id = body.get("qn_id")
    if not qn_id:
        return JsonResponse({'errno': 1003, 'errmsg': '问卷id不能为空'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if qn.qr_code is None or qn.qr_code == "":
        qn.generate_qr_code()
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'qrcode': settings.MEDIA_ROOT+qn.qr_code.url})
