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


# 列出组织联系人
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
    if not organization_id:
        return JsonResponse({'errno': 1003, 'errmsg': '组织id不能为空'})
    # 传入id对应的组织
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要查找的组织'})
    organization = Organization.objects.get(id=organization_id)
    # -1表示审核已拒绝且不可再加入 0表示审核中
    organization2user = Organization_2_User.objects.filter(organization=organization)
    list_organization2user = list(organization2user)
    if len(list_organization2user) == 0:
        return JsonResponse({'errno': 1005, 'errmsg': '本组织还没有联系人'})
    # 记录该组织内的User
    users_info = []
    for i in range(len(list_organization2user)):
        if list_organization2user[i].state >= 1:
            user = list_organization2user[i].user
            info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "state": list_organization2user[i].state
            }
            users_info.append(info)

    return JsonResponse({'errno': 0, 'errmsg': '列出组织联系人成功', 'list': users_info})


def organization_create_organization(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_name = body.get("organization_name")
    if not organization_name:
        return JsonResponse({'errno': 1003, 'errmsg': '组织名不能为空'})
    if Organization.objects.filter(name=organization_name).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '组织名已存在'})
    organization = Organization(name=organization_name)
    organization.save()
    organization2user = Organization_2_User(organization=organization, user=user, state=4)
    organization2user.save()
    return JsonResponse({'errno': 0, 'errmsg': '创建组织成功'})


def organization_invite(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    link = body.get("link")
    if link:
        if not decode_org_link(link):
            return JsonResponse({'errno': 1003, 'errmsg': '链接错误'})
        organization_id = decode_org_link(link)
    if not organization_id:
        return JsonResponse({'errno': 1004, 'errmsg': '组织id不能为空'})
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '不存在您想要邀请的组织'})
    organization = Organization.objects.get(id=organization_id)
    invitee_id = body.get("invitee_id")
    if not invitee_id:
        return JsonResponse({'errno': 1005, 'errmsg': '被邀请者不能为空'})
    invitee = None
    if User.objects.filter(id=invitee_id).exists():
        invitee = User.objects.get(id=invitee_id)
    if User.objects.filter(username=invitee_id).exists():
        invitee = User.objects.get(username=invitee_id)
    if User.objects.filter(email=invitee_id).exists():
        invitee = User.objects.get(email=invitee_id)
    if not invitee:
        return JsonResponse({'errno': 1006, 'errmsg': '不存在您想要邀请的用户'})
    if not Organization_2_User.objects.filter(organization=organization, user=user).exists():
        return JsonResponse({'errno': 1007, 'errmsg': '您不在该组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    state = organization2user.state
    # 判断当前登录用户是否有该组织的邀请权，当permission大于等于1时均有邀请权
    if state < 1 or state > 4:
        return JsonResponse({'errno': 1005, 'errmsg': '您的权限存在问题'})
    # 判断invitee是否已经在组织中
    if Organization_2_User.objects.filter(organization=organization, user=invitee).exists():
        organization2invitee = Organization_2_User.objects.get(organization=organization, user=invitee)
        if organization2invitee:
            state = organization2invitee.state
            if state == -1:
                return JsonResponse({'errno': 1006, 'errmsg': '该用户已被拒绝加入本组织'})
            elif state == 0:
                return JsonResponse({'errno': 1007, 'errmsg': '该用户的申请正在被审核'})
            elif state == -2:
                return JsonResponse({'errno': 1008, 'errmsg': '该用户尚未同意邀请'})
            else:
                return JsonResponse({'errno': 1008, 'errmsg': '该用户已经在本组织中'})
    # 此时用户有权限、有受邀者和想要邀请的组织，此时state=0代表审核中
    invitation = Organization_2_User.objects.create(organization=organization, user=invitee, state=-2)
    Message.objects.create(user=invitee, message="您已被邀请加入组织" + organization.name + "，请尽快处理", type=1)
    return JsonResponse({'errno': 0, 'errmsg': '已邀请'})


# 生成组织邀请链接
def organization_generate_link(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    if not organization_id:
        return JsonResponse({'errno': 1003, 'errmsg': '组织id不能为空'})
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要邀请的组织'})
    organization = Organization.objects.get(id=organization_id)
    if not Organization_2_User.objects.filter(organization=organization, user=user).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '您不在该组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    state = organization2user.state
    # 判断当前登录用户是否有该组织的邀请权，当permission大于等于1时均有邀请权
    if state < 1 or state > 4:
        return JsonResponse({'errno': 1006, 'errmsg': '您的权限存在问题'})
    # 生成链接
    link = organization.link
    if link is None:
        link = organization.generate_link()
        organization.link = link
        organization.save()
    return JsonResponse({'errno': 0, 'errmsg': '生成链接成功', 'link': link})


# 列出未审核名单
def organization_list_unreviewed_list(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    if organization_id is None:
        return JsonResponse({'errno': 1003, 'errmsg': '组织id不能为空'})
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要通过申请的组织'})
    organization = Organization.objects.get(id=organization_id)
    if not Organization_2_User.objects.filter(organization=organization, user=user).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '您不在该组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    state = organization2user.state
    if state < 3:
        return JsonResponse({'errno': 1006, 'errmsg': '您没有审核权限'})
    return_list = []
    for organization2user in Organization_2_User.objects.filter(organization=organization, state=0):
        return_list.append({'id': organization2user.user.id, 'username': organization2user.user.name,
                            'email': organization2user.user.email})
    return JsonResponse({'errno': 0, 'errmsg': '列出未审核名单成功', 'list': return_list})


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
    if organization_id is None:
        return JsonResponse({'errno': 1003, 'errmsg': '组织id不能为空'})
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要通过申请的组织'})
    organization = Organization.objects.get(id=organization_id)
    if not Organization_2_User.objects.filter(organization=organization, user=user).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '您不在该组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    state = organization2user.state
    if state < 3:
        return JsonResponse({'errno': 1006, 'errmsg': '您没有审核权限'})
    invitee_id = body.get("invitee_id")
    if invitee_id is None:
        return JsonResponse({'errno': 1007, 'errmsg': '被邀请人id不能为空'})
    if not User.objects.filter(id=invitee_id).exists():
        return JsonResponse({'errno': 1008, 'errmsg': '不存在您想要邀请的用户'})
    invitee = User.objects.get(id=invitee_id)
    # 是否同意，同意为1，不同意为0
    if_agree = body.get("if_agree")
    if if_agree is None:
        return JsonResponse({'errno': 1009, 'errmsg': '是否同意不能为空'})
    if if_agree != 1 and if_agree != 0:
        return JsonResponse({'errno': 1010, 'errmsg': '是否同意参数错误'})
    if not Organization_2_User.objects.filter(organization=organization, user=invitee).exists():
        return JsonResponse({'errno': 1011, 'errmsg': '该用户未收到申请'})
    organization2invitee = Organization_2_User.objects.get(organization=organization, user=invitee)
    state = organization2invitee.state
    if state == -1:
        return JsonResponse({'errno': 1012, 'errmsg': '该用户已被拒绝加入本组织'})
    elif state >= 1:
        return JsonResponse({'errno': 1013, 'errmsg': '该用户已经在本组织中'})
    elif state == -2:
        return JsonResponse({'errno': 1014, 'errmsg': '该用户尚未同意邀请'})
    if if_agree == 1:
        organization2invitee.state = 1
        organization2invitee.save()
        Message.objects.create(user=invitee, message="您已被同意加入组织" + organization.name, type=8)
    elif if_agree == 0:
        organization2invitee.state = -1
        organization2invitee.save()
        Message.objects.create(user=invitee, message="您已被拒绝加入组织" + organization.name, type=8)
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
    if organization_id is None:
        return JsonResponse({'errno': 1003, 'errmsg': '组织id不能为空'})
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '不存在您想要通过申请的组织'})
    organization = Organization.objects.get(id=organization_id)
    if not Organization_2_User.objects.filter(organization=organization, user=user).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '您不在该组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    state = organization2user.state
    if state < 3:
        return JsonResponse({'errno': 1006, 'errmsg': '您没有审核权限'})
    kicked_id = body.get("kicked_id")
    if kicked_id is None:
        return JsonResponse({'errno': 1007, 'errmsg': '被踢人id不能为空'})
    if not User.objects.filter(id=kicked_id).exists():
        return JsonResponse({'errno': 1008, 'errmsg': '不存在您想要踢的用户'})
    kicked = User.objects.get(id=kicked_id)
    if not Organization_2_User.objects.filter(organization=organization, user=kicked_id).exists():
        return JsonResponse({'errno': 1009, 'errmsg': '该用户不在本组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=kicked)
    state2 = organization2user.state
    if state2 > state:
        return JsonResponse({'errno': 1010, 'errmsg': '您没有权限踢出该用户'})
    organization2user.state = -1
    organization2user.save()
    Message.objects.create(user=kicked, message="您已被踢出组织" + organization.name, type=2)
    return JsonResponse({'errno': 0, 'errmsg': '踢出业务处理结束'})


def organization_grant(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    if organization_id is None:
        return JsonResponse({'errno': 1003, 'errmsg': '组织id不能为空'})
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '您不在组织中'})
    organization = Organization.objects.get(id=organization_id)
    if not Organization_2_User.objects.filter(organization=organization, user=user).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '您不在该组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    state = organization2user.state
    if state < 3:
        return JsonResponse({'errno': 1006, 'errmsg': '您没有权限'})
    grant_level = body.get("grant_id")
    grantee_id = body.get("grantee_id")
    if not grantee_id:
        return JsonResponse({'errno': 1007, 'errmsg': '被授权人id不能为空'})
    if not grant_level:
        return JsonResponse({'errno': 1008, 'errmsg': '被赋予权限不能为空'})
    if grant_level not in [1, 2, 3, 4]:
        return JsonResponse({'errno': 1009, 'errmsg': '被赋予权限不合法'})
    if not User.objects.filter(id=grantee_id).exists():
        return JsonResponse({'errno': 1010, 'errmsg': '不存在您想要赋予权限的用户'})
    grantee = User.objects.get(id=grantee_id)
    if not Organization_2_User.objects.filter(organization=organization, user=grantee).exists():
        return JsonResponse({'errno': 1011, 'errmsg': '该用户不在本组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=grantee)
    if organization2user.state > state:
        return JsonResponse({'errno': 1012, 'errmsg': '您没有权限赋予该用户权限'})
    power = ["普通成员", "发布一次问卷", "管理员", "创建者"]
    if state == 3:
        if grant_level > 2:
            return JsonResponse({'errno': 1013, 'errmsg': '您没有权限赋予该用户权限'})
        else:
            organization2user.state = grant_level
            organization2user.save()
            Message.objects.create(user=grantee,
                                   message="您已被赋予" + organization.name + "的权限,权限为" + power[grant_level],
                                   type=3)
    if state == 4:
        organization2user.state = grant_level
        organization2user.save()
        Message.objects.create(user=grantee,
                               message="您已被赋予" + organization.name + "的权限,权限为" + power[grant_level], type=3)
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
    organization = None
    if organization_id is not None:
        if not Organization.objects.filter(id=organization_id).exists():
            return JsonResponse({'errno': 1003, 'errmsg': '不存在您想要查询的组织'})
        organization = Organization.objects.get(id=organization_id)
    search_content = body.get("search_content")
    if not search_content:
        return JsonResponse({'errno': 1004, 'errmsg': '搜索内容不能为空'})
    return_list = []
    if organization is not None:
        temp_list = Organization_2_User.objects.filter(organization = organization)
        for temp in temp_list:
            if search_content in temp.user.username or search_content in temp.user.email or search_content in temp.user.id:
                return_list.append({"user_id": temp.user.id, "user_name": temp.user.username, "user_email": temp.user.email})
    else:
        temp_list = Organization_2_User.objects.filter(user = user)
        for temp in temp_list:
            if search_content in temp.organization.name or search_content in temp.organization.id:
                return_list.append({"organization_id": temp.organization.id, "organization_name": temp.organization.name})
    return JsonResponse({'errno': 0, 'errmsg': '查询信息成功', 'return_list': return_list})


def organization_disband(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    if organization_id is None:
        return JsonResponse({'errno': 1003, 'errmsg': '组织id不能为空'})
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '您不在组织中'})
    organization = Organization.objects.get(id=organization_id)
    if not Organization_2_User.objects.filter(organization=organization, user=user).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '您不在该组织中'})
    organization2user = Organization_2_User.objects.get(organization=organization, user=user)
    state = organization2user.state
    if state != 4:
        return JsonResponse({'errno': 1006, 'errmsg': '您没有权限'})
    for organization2user in Organization_2_User.objects.filter(organization=organization):
        if organization2user.state >= 1:
            Message.objects.create(user=organization2user.user, message="组织" + organization.name + "已解散", type=4)
    organization.delete()
    return JsonResponse({'errno': 0, 'errmsg': '解散组织成功'})


def organization_approve_join(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    organization_id = body.get("organization_id")
    if organization_id is None:
        return JsonResponse({'errno': 1003, 'errmsg': '组织id不能为空'})
    if not Organization_2_User.objects.filter(organization_id=organization_id, user=user).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '您已经未收到邀请'})
    organization2user = Organization_2_User.objects.get(organization_id=organization_id, user=user)
    approved = body.get("approved")
    # 1 同意 0 拒绝
    if approved is None:
        return JsonResponse({'errno': 1005, 'errmsg': '是否同意不能为空'})
    if organization2user.state != -2:
        return JsonResponse({'errno': 1005, 'errmsg': '您已经在组织中或无法再加入或已同意申请'})
    if approved == 0:
        organization2user.state = -1
        organization2user.save()
        return JsonResponse({'errno': 0, 'errmsg': '拒绝申请成功'})
    organization2user.state = 0
    organization2user.save()
    for organization2user in Organization_2_User.objects.filter(organization_id=organization_id):
        if organization2user.state >= 3:
            Message.objects.create(user=organization2user.user, message="用户" + user.username + "的加入申请待审核", type=4)
    return JsonResponse({'errno': 0, 'errmsg': '同意申请成功'})

def message_list(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    messages = Message.objects.filter(user=user)
    info = []
    for message in messages:
        info.append({
            "id": message.id,
            "message": message.message,
            "type": message.type,
        })
    return JsonResponse({'errno': 0, 'errmsg': '查询信息成功', 'info': info})


def message_delete(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    message_id = body.get("message_id")
    if message_id is None:
        return JsonResponse({'errno': 1002, 'errmsg': '消息id不能为空'})
    if not Message.objects.filter(id=message_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '消息不存在'})
    message = Message.objects.get(id=message_id)
    message.delete()
    return JsonResponse({'errno': 0, 'errmsg': '删除成功'})


