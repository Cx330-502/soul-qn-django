from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from Qn.models import *
import json


# Create your views here.


def hello(request):
    return JsonResponse({'message': 'Hello, world!'})


#-1列出个人发布问卷 -2列出回答的问卷 -3列出回收站的问卷 >=0列出团体发布问卷
def list_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    userid = user.id
    current_status = body.get("current_status")
    # -1：在个人发布的问卷页面 -2：在回答的问题页面 -3：在回收站页面 >=0：在组织发布的问卷页面（为组织编号）
    if not current_status:
        return JsonResponse({'errno': 1003, 'errmsg': '当前状态不能为空'})
    if current_status == -1:
        # 在个人发布的问卷页面
        user_questionnaire = User_create_Questionnaire.objects.filter(user_id = userid)
        # 转化成数组
        list_questionnaire = list(user_questionnaire)
        if len(list_questionnaire) == 0:
            return JsonResponse({'errno': 1004, 'errmsg': '当前用户没有创建问卷'})
    elif current_status == -2:
        # 在回答的问题页面
        user_answer_questionnaire = Answer_sheet.objects.filter(answerer_id=userid)
        list_questionnaire = list(user_answer_questionnaire)
        if len(list_questionnaire == 0):
            return JsonResponse({'errno': 1005, 'errmsg': '当前用户没有已经作答的问卷'})
    elif current_status == -3:
        # 在回收站页面
        user_delete_questionnaire =

    elif current_status >= 0:
        # 在组织发布的问卷页面，current_status为组织id
        organization = Organization.objects.get(id = current_status)
        if not organization:
            return JsonResponse({'errno': 1006, 'errmsg': '不存在这个组织'})
        # 存在该组织，在组织创建问卷中取得QuerySet
        organization_questionnaire = Organization_create_Questionnaire.objects.filter(organization_id= current_status)
        list_questionnaire = list(organization_questionnaire)
        if len(list_questionnaire) == 0:
            return JsonResponse({'errno': 1007, 'errmsg': '当前组织没有发布过问卷'})

    for i in range(len(list_questionnaire)):
        # 读当前用户创建的问卷id
        questionnaireid = list_questionnaire[i].questionnaire_id
        questinnaire = Questionnaire.objects.get(id=questionnaireid)
        list_questionnaire[i] = {
            "name": questinnaire.name,
            "type": questinnaire.type,
            "public": questinnaire.public,
            "permission": questinnaire.permission,
            "collection_num": questinnaire.collection_num,
            "state": questinnaire.state,
            "release_time": questinnaire.release_time,
            "finish_time": questinnaire.finish_time,
            "start_time": questinnaire.start_time,
            "duration": questinnaire.duration,
            # "password": questinnaire.password,
            "title": questinnaire.title,
            "description": questinnaire.description,
            "link": questinnaire.link,
            "qr_code": questinnaire.qr_code
        }
    return JsonResponse({'errno': 0, 'errmsg': '查询问卷成功', 'list': list_questionnaire})
def list_organization(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    userid = user.id
    # -1为审核已拒绝且不可再加入 0为审核中 所有大于0的值都说明当前用户已经加入组织
    user_organization = Organization_2_User.objects.filter(user_id = userid, state__gt = 0)
    organization = list(user_organization)
    if len(organization) == 0:
        return JsonResponse({'errno': 1003, 'errmsg': '当前用户没有加入任何组织'})

    # for i in range(len(organization)):


    return JsonResponse({'errno': 0, 'errmsg': '查询组织成功'})

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
