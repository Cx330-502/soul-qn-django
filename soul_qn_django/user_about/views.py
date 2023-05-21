import re
from base64 import b64encode, b64decode
from hashlib import sha256

from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from Qn.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import user_about.extra_codes.captcha as captchaclass
import json


def encrypt(data, key):
    f = Fernet(key)
    decrypted_data = f.encrypt(data.encode())
    return decrypted_data.decode()


def decrypt(data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(data.encode())
    return decrypted_data.decode()


# Create your views here.
# 发送验证码的视图函数，由前端检查验证码是否正确
@csrf_exempt
def captcha(request):
    key = b'2L0QpUEp09cO-9B8FhZ0eqkTLiw1mZDv6_U7nhGGZho='
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    receiver_email = body.get("email")
    try:
        validate_email(receiver_email)
    except ValidationError:
        return JsonResponse({'errno': 1002, 'errmsg': '邮箱不符合规范'})
    verification = captchaclass.SendEmail(data=captchaclass.data, receiver=receiver_email).send_email()
    verification = encrypt(verification, key)
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
    if not username:
        return JsonResponse({'errno': 1002, 'errmsg': '用户名不能为空'})
    if not password:
        return JsonResponse({'errno': 1003, 'errmsg': '密码不能为空'})
    if not email:
        return JsonResponse({'errno': 1004, 'errmsg': '邮箱不能为空'})
    if not re.match(r"^[a-zA-Z0-9_-]{4,16}$", username):
        return JsonResponse({'errno': 1005, 'errmsg': '用户名不符合规范'})
    if not re.match(r"^[a-zA-Z0-9_-]{6,16}$", password):
        return JsonResponse({'errno': 1006, 'errmsg': '密码不符合规范'})
    if User.objects.filter(username=username).exists():
        return JsonResponse({'errno': 1007, 'errmsg': '用户名已存在'})
    if User.objects.filter(email=email).exists():
        return JsonResponse({'errno': 1008, 'errmsg': '邮箱已存在'})
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
        return JsonResponse({'errno': 1002, 'errmsg': '用户名或邮箱不存在'})
    if user.password == password:
        token = user.create_token(3600 * 24)
        return JsonResponse({'errno': 0, 'errmsg': '登录成功', 'token': token})
    return JsonResponse({'errno': 1003, 'errmsg': '密码错误'})


# 一个token测试的视图函数，前端传入token，后端验证token是否正确
@csrf_exempt
def test_login(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    print(token)
    user = auth_token(token)
    if user:
        return JsonResponse({'errno': 0, 'errmsg': '登录成功'})
    return JsonResponse({'errno': 1001, 'errmsg': '登录失败'})


def organization_list_user(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    userid = user.id
    organization_id = body.get("id")
    # 传入id对应的组织
    organization = Organization.objects.get(id = organization_id)
    if not organization:
        return JsonResponse({'errno': 1003, 'errmsg': '不存在您想要查找的组织'})
    # -1表示审核已拒绝且不可再加入 0表示审核中
    organization2user = Organization_2_User.objects.filter(organization = organization, state__gt = 0)
    list_organization2user = list(organization2user)
    if len(list_organization2user) == 0:
        return JsonResponse({'errno': 1004, 'errmsg': '本组织还没有联系人'})
    # 记录该组织内的User
    users = []
    users_info = []
    for i in range(len(list_organization2user)):
        user = list_organization2user[i].user
        users.append(user)

    for user in users:
        info = {
            "username" : user.username
        }
        users_info.append(info)

    return JsonResponse({'errno': 0, 'errmsg': '列出组织联系人成功', 'list': users_info})

def organization_invite(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    invitee_id = body.get("invitee_id")
    organization = Organization.objects.get(id = organization_id)
    invitee = User.objects.get(id = invitee_id)
    if not organization:
        return JsonResponse({'errno': 1003, 'errmsg': '不存在您想要邀请的组织'})
    permission = Organization_2_User.objects.get(organization = organization, user = user).state
    if not invitee:
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要邀请的用户'})
    # 判断当前登录用户是否有该组织的邀请权，当permission大于等于1时均有邀请权
    if permission < 1 or permission > 4:
        return JsonResponse({'errno': 1005, 'errmsg': '您的权限存在问题'})
    # 判断invitee是否已经在组织中
    organization2invitee = Organization_2_User.objects.get(organization = organization, user = invitee)
    if organization2invitee:
        state = organization2invitee.state
        if state == -1:
            return JsonResponse({'errno': 1006, 'errmsg': '该用户已被拒绝加入本组织'})
        elif state == 0:
            return JsonResponse({'errno': 1007, 'errmsg': '该用户的申请正在被审核'})
        else:
            return JsonResponse({'errno': 1008, 'errmsg': '该用户已经在本组织中'})
    # 此时用户有权限、有受邀者和想要邀请的组织，此时state=0代表审核中
    invitation = Organization_2_User(organization = organization, user = invitee, state = 0)
    Organization_2_User.save(invitation)
    return JsonResponse({'errno': 0, 'errmsg': '已邀请'})

# 通过加入申请
def organization_pass(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    invitee_id = body.get("invitee_id")
    # 是否同意，同意为1，不同意为-1
    if_agree = body.get("if_agree")
    organization = Organization.objects.get(id=organization_id)
    invitee = User.objects.get(id=invitee_id)
    if not organization:
        return JsonResponse({'errno': 1003, 'errmsg': '不存在您想要通过申请的组织'})
    if not invitee:
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要邀请的用户'})

    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    if not organization2user:
        return JsonResponse({'errno': 1005, 'errmsg': '您还不在该组织中'})
    permission = organization2user.state
    if permission == 0 or permission == 1:
        return JsonResponse({'errno': 1005, 'errmsg': '您还不在该组织中'})

    organization2invitee = Organization_2_User.objects.get(organization=organization, user=invitee)
    if not organization2invitee:
        return JsonResponse({'errno': 1006, 'errmsg': '该用户还没有收到邀请'})
    if organization2invitee:
        state = organization2invitee.state
        if state == -1:
            return JsonResponse({'errno': 1007, 'errmsg': '该用户已被拒绝加入本组织'})
        elif state >= 1:
            return JsonResponse({'errno': 1008, 'errmsg': '该用户已经在本组织中'})

    # 判断是否当前用户是否有权限通过，仅有3、4级用户可以通过加入申请
    if permission < 3 or permission > 4:
        return JsonResponse({'errno': 1009, 'errmsg': '您的权限存在问题'})
    organization2invitee.state = if_agree
    organization2invitee.save()
    return JsonResponse({'errno': 0, 'errmsg': '加入申请业务处理结束'})

def organization_kick(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    invitee_id = body.get("invitee_id")
    organization = Organization.objects.get(id=organization_id)
    invitee = User.objects.get(id=invitee_id)
    if not organization:
        return JsonResponse({'errno': 1003, 'errmsg': '不存在您想要移除用户的组织'})
    if not invitee:
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要移除的用户'})

    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    if not organization2user:
        return JsonResponse({'errno': 1005, 'errmsg': '您还不在该组织中'})
    permission = organization2user.state
    if permission == 0 or permission == -1:
        return JsonResponse({'errno': 1006, 'errmsg': '您还不在该组织中'})
    organization2invitee = Organization_2_User.objects.get(organization=organization, user=invitee)
    if not organization2invitee:
        return JsonResponse({'errno': 1007, 'errmsg': '该用户还不在本组织中'})
    if organization2invitee:
        state = organization2invitee.state
        if state == -1:
            return JsonResponse({'errno': 1008, 'errmsg': '该用户已被拒绝加入本组织'})
        elif state == 0:
            return JsonResponse({'errno': 1009, 'errmsg': '该用户正在被审核'})
        elif state == 1:
            # 要踢的人是一级的
            if permission >= 3:
                organization2invitee.state = -1;
                organization2invitee.save()
            else:
                return JsonResponse({'errno': 1010,'errmsg': '您的权限不允许'})
        elif state == 2 or state == 3:
            if permission == 4:
                organization2invitee.state = -1;
                organization2invitee.save()
            else:
                return JsonResponse({'errno': 1010,'errmsg': '您的权限不允许'})

    return JsonResponse({'errno': 0, 'errmsg': '已经踢人成功'})

def organization_grant(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    invitee_id = body.get("invitee_id")
    level = body.get("level")
    organization = Organization.objects.get(id=organization_id)
    invitee = User.objects.get(id=invitee_id)
    if not organization:
        return JsonResponse({'errno': 1003, 'errmsg': '不存在您想要赋予用户权限的组织'})
    if not invitee:
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要赋予权限的用户'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    if not organization2user:
        return JsonResponse({'errno': 1005, 'errmsg': '您还不在该组织中'})
    permission = organization2user.state
    if permission == 0 or permission == -1:
        return JsonResponse({'errno': 1006, 'errmsg': '您还不在该组织中'})
    organization2invitee = Organization_2_User.objects.get(organization=organization, user=invitee)
    if not organization2invitee:
        return JsonResponse({'errno': 1007, 'errmsg': '该用户还不在本组织中'})
    if organization2invitee:
        state = organization2invitee.state
        if state == -1:
            return JsonResponse({'errno': 1008, 'errmsg': '该用户已被拒绝加入本组织'})
        elif state == 0:
            return JsonResponse({'errno': 1009, 'errmsg': '该用户正在被审核'})
    # 该用户已经加入本组织中
    if level == 2:
        if permission >= 3:
            organization2invitee.state = level
            organization2invitee.save()
        else:
            return JsonResponse({'errno': 1010, 'errmsg': '您的权限不够'})
    elif level == 3:
        if permission == 4:
            organization2invitee.state = level
            organization2invitee.save()
        else:
            return JsonResponse({'errno': 1010, 'errmsg': '您的权限不够'})

    return JsonResponse({'errno': 0, 'errmsg': '已经成功赋予权限'})

def organization_search(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    organization = Organization.objects.get(id = organization_id)
    if not organization:
        return JsonResponse({'errno': 1003, 'errmsg': '不存在您想要查询的组织'})
    info = {
        "name" : organization.name
    }
    return JsonResponse({'errno': 0, 'errmsg': '查询信息成功', 'info': info})

def organization_disband(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    organization = Organization.objects.get(id=organization_id)
    if not organization:
        return JsonResponse({'errno': 1003, 'errmsg': '不存在您想要解散的组织'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    if not organization2user:
        return JsonResponse({'errno': 1005, 'errmsg': '您还不在该组织中'})
    permission = organization2user.state
    if permission == 0 or permission == -1:
        return JsonResponse({'errno': 1006, 'errmsg': '您还不在该组织中'})
    if permission >=1 and permission <=3:
        return JsonResponse({'errno': 1007, 'errmsg': '您的权限不够'})
    if permission == 4:
        try:
            organization.delete()
        except Exception as e:
            print(e)
    return JsonResponse({'errno': 0, 'errmsg': '解散组织成功'})
