from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from Qn.models import *
import json
import shutil

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
        # 在个人发布的问卷页面查询已发布的问卷
        user_questionnaire = User_create_Questionnaire.objects.filter(user = userid)
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
    list_user_organization = list(user_organization)
    if len(list_user_organization) == 0:
        return JsonResponse({'errno': 1003, 'errmsg': '当前用户没有加入任何组织'})

    for i in range(len(list_user_organization)):
        organization_id = list_user_organization[i].organization
        organization = Organization.objects.get(id=organization_id)
        list_user_organization[i] = {
            "name": organization.name
        }

    return JsonResponse({'errno': 0, 'errmsg': '查询组织成功', 'list': list_user_organization})

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
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'qrcode': settings.MEDIA_ROOT + qn.qr_code.url})


# 将问卷放入回收站
def remove_qn(request):
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
    if User_create_Questionnaire.objects.filter(user=user, questionnaire=qn).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '用户没有权限'})
    qn.state = -3
    qn.save()
    return JsonResponse({'errno': 0, 'errmsg': '成功'})


# 删除问卷
def delete_qn(request):
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
    organization_id = body.get("organization_id")
    if not organization_id:
        qn.delete()
        path = settings.MEDIA_ROOT + '/questionnaire/' + str(qn_id)
        if os.path.exists(path):
            shutil.rmtree(path)
        return JsonResponse({'errno': 0, 'errmsg': '成功'})
    if not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '组织不存在'})
    organization = Organization.objects.get(id=organization_id)
    if not Organization_create_Questionnaire.objects.filter(organization=organization,
                                                            questionnaire=qn).exists():
        return JsonResponse({'errno': 1006, 'errmsg': '组织未发布该问卷'})
    if Organization_2_User.objects.filter(organization=organization, user=user).exists():
        return JsonResponse({'errno': 1007, 'errmsg': '用户不是该组织成员'})
    orz_2_user = Organization_2_User.objects.get(organization=organization, user=user)
    if orz_2_user.role <= 2:
        return JsonResponse({'errno': 1008, 'errmsg': '用户没有权限'})
    qn.delete()
    path = settings.MEDIA_ROOT + '/questionnaire/' + str(qn_id)
    if os.path.exists(path):
        shutil.rmtree(path)
    return JsonResponse({'errno': 0, 'errmsg': '成功'})


def search_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    search_content = body.get("search_content")
    if not search_content:
        return JsonResponse({'errno': 1003, 'errmsg': '搜索内容不能为空'})
    current_status = body.get("current_status")
    # -1:在个人发布的问卷页面 -2:在回答的问卷页面 -3:在回收站页面 >=0: 在组织发布的问卷页面(为组织编号)
    if not current_status:
        return JsonResponse({'errno': 1004, 'errmsg': '当前状态不能为空'})
    all_qn_list = None
    qn_list = []
    if current_status >= 0:
        if not Organization.objects.filter(id=current_status).exists():
            return JsonResponse({'errno': 1005, 'errmsg': '组织不存在'})
        organization = Organization.objects.get(id=current_status)
        all_qn_list = Organization_create_Questionnaire.objects.filter(organization=organization)
        for object0 in all_qn_list:
            qn = object0.questionnaire
            if qn.state != -3:
                qn_list.append(qn)
    elif current_status == -1:
        all_qn_list = User_create_Questionnaire.objects.filter(user=user)
        for object0 in all_qn_list:
            qn = object0.questionnaire
            if qn.state != -3:
                qn_list.append(qn)
    elif current_status == -2:
        all_qn_list = Answer_sheet.objects.filter(user=user)
        for object0 in all_qn_list:
            qn = object0.questionnaire
            if qn.state != -3:
                qn_list.append(qn)
    elif current_status == -3:
        all_qn_list = User_create_Questionnaire.objects.filter(user=user)
        for object0 in all_qn_list:
            qn = object0.questionnaire
            if qn.state == -3:
                qn_list.append(qn)
    return_list = []
    for qn in qn_list:
        flag = False
        if search_content in qn.title:
            flag = True
        elif search_content in qn.description:
            flag = True
        elif search_content in qn.name:
            flag = True
        if flag:
            background_image = settings.MEDIA_ROOT + examples_list[i].background_image.url if examples_list[
                i].background_image else None
            header_image = settings.MEDIA_ROOT + examples_list[i].header_image.url if examples_list[
                i].header_image else None
            qn_info = {"title": examples_list[i].title, "id": examples_list[i].id,
                       "description": examples_list[i].description,
                       "background_image": background_image, "header_image": header_image,
                       "font_color": examples_list[i].font_color,
                       "header_font_color": examples_list[i].header_font_color,
                       "name": examples_list[i].name
                       }
            return_list.append(qn_info)
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'qn_list': return_list})


def sort_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    sort_method = body.get("sort_method")
    # 排序方法为1:按发布时间排序
    # 排序方法为2:按回答人数排序
    # 排序方法为3:按名称排序
    # 排序方法为4:按开启状态
    # 排序方法为5:按截止时间
    if not sort_method:
        return JsonResponse({'errno': 1002, 'errmsg': '排序方法不能为空'})
    sort_method_type = body.get("sort_method_type")
    # 排序方法类型为1:升序
    # 排序方法类型为2:降序
    if not sort_method_type:
        return JsonResponse({'errno': 1003, 'errmsg': '排序方法类型不能为空'})
    qn_id_list = body.get("qn_id_list")
    if not qn_id_list:
        return JsonResponse({'errno': 1003, 'errmsg': '问卷id列表不能为空'})
    qn_list = []
    for qn_id in qn_id_list:
        if not Questionnaire.objects.filter(id=qn_id).exists():
            return JsonResponse({'errno': 1004, 'errmsg': '问卷不存在'})
        qn_list.append(Questionnaire.objects.get(id=qn_id))
    if sort_method == 1:
        qn_list.sort(key=lambda x: x.release_time, reverse=True if sort_method_type == 2 else False)
    elif sort_method == 2:
        qn_list.sort(key=lambda x: x.collection_num, reverse=True if sort_method_type == 2 else False)
    elif sort_method == 3:
        qn_list.sort(key=lambda x: x.name, reverse=True if sort_method_type == 2 else False)
    elif sort_method == 4:
        qn_list.sort(key=lambda x: x.state, reverse=True if sort_method_type == 2 else False)
    elif sort_method == 5:
        qn_list.sort(key=lambda x: x.finish_time, reverse=True if sort_method_type == 2 else False)
    return_list = []
    for qn in qn_list:
        background_image = settings.MEDIA_ROOT + examples_list[i].background_image.url if examples_list[
            i].background_image else None
        header_image = settings.MEDIA_ROOT + examples_list[i].header_image.url if examples_list[
            i].header_image else None
        qn_info = {"title": examples_list[i].title, "id": examples_list[i].id,
                   "description": examples_list[i].description,
                   "background_image": background_image, "header_image": header_image,
                   "font_color": examples_list[i].font_color,
                   "header_font_color": examples_list[i].header_font_color,
                   "name": examples_list[i].name
                   }
        return_list.append(qn_info)
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'qn_list': return_list})


def copy_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_id = body.get("qn_id")
    if not qn_id:
        return JsonResponse({'errno': 1002, 'errmsg': '问卷id不能为空'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if not qn.header_image:
        header_image = None
    else:
        try:
            with open(question_image, 'rb') as f:
                file_content = f.read()
                file_name = f.name.split('/')[-1]
                header_image = ContentFile(file_content, file_name)
        except Exception as e:
            print(e)
            header_image = None
    if not qn.background_image:
        background_image = None
    else:
        try:
            with open(question_image, 'rb') as f:
                file_content = f.read()
                file_name = f.name.split('/')[-1]
                background_image = ContentFile(file_content, file_name)
        except Exception as e:
            print(e)
            background_image = None
    new_qn = Questionnaire.objects.create(name=qn.name, title=qn.title, public=qn.public,
                                          permission=qn.permission, collection_num=0,
                                          state=0, release_time=null, finish_time=null,
                                          start_time=null, duration=qn.duration,
                                          password=qn.password, description=qn.description,
                                          header_image=header_image,
                                          background_image=background_image,
                                          font_color=qn.font_color,
                                          header_font_color=qn.header_font_color,
                                          question_num_visible=qn.question_num_visible)
    User_create_Questionnaire.objects.create(user=user, questionnaire=new_qn)
    if not Question.objects.filter(questionnaire=qn).exists():
        return JsonResponse({'errno': 0, 'errmsg': '成功'})
    questions = Question.objects.filter(questionnaire=qn)
    for question in questions:
        if not question.video:
            video = None
        else:
            try:
                with open(question.video, 'rb') as f:
                    file_content = f.read()
                    file_name = f.name.split('/')[-1]
                    video = ContentFile(file_content, file_name)
            except Exception as e:
                print(e)
                video = None
        if not question.image:
            image = None
        else:
            try:
                with open(question.image, 'rb') as f:
                    file_content = f.read()
                    file_name = f.name.split('/')[-1]
                    image = ContentFile(file_content, file_name)
            except Exception as e:
                print(e)
                image = None
        new_question = Question.objects.create(type=question.type, description=question.description,
                                               questionnaire=new_qn, necessary=question.necessary,
                                               surface=question.surface, width=question.width,
                                               order=question.order, change_line=question.change_line,
                                               score=question.score, content1=question.content1,
                                               content2=question.content2, video=video, image=image,
                                               answer1=question.answer1, answer2=question.answer2,
                                               num_limit=question.num_limit,
                                               multi_lines=question.multi_lines,
                                               unit=question.unit)
    return JsonResponse({'errno': 0, 'errmsg': '成功'})

def open_qn(request):
    body = json.loads(request.body)
    qn_id = body.get("qn_id")
    if not qn_id:
        return JsonResponse({'errno': 1001, 'errmsg': '问卷id不能为空'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1002, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    qn.state = 1
    qn.release_time = datetime.now()
    qn.save()
    return JsonResponse({'errno': 0, 'errmsg': '开启成功'})


def close_qn(request):
    body = json.loads(request.body)
    qn_id = body.get("qn_id")
    if not qn_id:
        return JsonResponse({'errno': 1001, 'errmsg': '问卷id不能为空'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1002, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    qn.state = 0
    qn.finish_time = datetime.now()
    qn.save()
    return JsonResponse({'errno': 0, 'errmsg': '关闭成功'})
