import base64
import os
from datetime import datetime
import urllib.parse
import requests
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from Qn.models import *
from django.conf import settings


# Create your views here.
# 获得十个样例问卷
@csrf_exempt
def get_examples(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_type = body.get("type")
    if qn_type is None:
        return JsonResponse({'errno': 1003, 'errmsg': '类型不能为空'})
    if not Questionnaire.objects.filter(public=True).filter(type=qn_type).exists():
        return JsonResponse({'errno': 1, 'errmsg': '无同类型问卷', 'examples': []})
    organization_id = body.get("organization_id")
    if organization_id:
        if not Organization.objects.filter(id=organization_id).exists():
            return JsonResponse({'errno': 1004, 'errmsg': '组织不存在'})
        if not Organization_2_User.objects.filter(
                organization=organization_id).filter(user=user).exists():
            return JsonResponse({'errno': 1005, 'errmsg': '用户不在该组织'})
        if Organization_2_User.objects.get(organization=organization_id, user=user).state < 2:
            return JsonResponse({'errno': 1006, 'errmsg': '无权限'})
    examples = Questionnaire.objects.filter(type=qn_type)[:10]
    examples_list = list(examples)
    for i in range(len(examples_list)):
        background_image = settings.MEDIA_ROOT + examples_list[i].background_image.url if examples_list[
            i].background_image else None
        header_image = settings.MEDIA_ROOT + examples_list[i].header_image.url if examples_list[
            i].header_image else None
        examples_list[i] = {"title": examples_list[i].title, "id": examples_list[i].id,
                            "description": examples_list[i].description,
                            "background_image": background_image, "header_image": header_image,
                            "font_color": examples_list[i].font_color,
                            "header_font_color": examples_list[i].header_font_color,
                            "name": examples_list[i].name
                            }
    return JsonResponse({'errno': 0, 'errmsg': '获取成功', 'examples': examples_list})


# 获得id对应的模板进行预览、或在此基础上进行复制
@csrf_exempt
def preview_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    example_id = body.get("qn_id")
    if example_id is None:
        return JsonResponse({'errno': 1, 'errmsg': '无问卷模板', 'qn': {}})
    if not Questionnaire.objects.filter(id=example_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷模板不存在'})
    example = Questionnaire.objects.get(id=example_id)
    background_image = settings.MEDIA_ROOT + example.background_image.url if example.background_image else None
    header_image = settings.MEDIA_ROOT + example.header_image.url if example.header_image else None
    qn = {'title': example.title, 'description': example.description, 'type': example.type,
          'permission': example.permission, 'questions': [],
          'public': example.permission, 'name': example.name,
          'background_image': background_image, 'header_image': header_image,
          'font_color': example.font_color, 'header_font_color': example.header_font_color,
          'question_num_visible': example.question_num_visible, 'duration': example.duration}
    questions = Question.objects.filter(questionnaire=example).all()
    for question in questions:
        video_data = settings.MEDIA_ROOT + question.video.url if question.video else None
        image_data = settings.MEDIA_ROOT + question.image.url if question.image else None
        qn['questions'].append({'type': question.type, 'description': question.description,
                                'necessary': question.necessary, 'surface': question.surface,
                                'width': question.width, 'order': question.order,
                                'change_line': question.change_line, 'score': question.score,
                                'content1': question.content1, 'content2': question.content2,
                                'video': video_data, 'image': image_data,
                                'answer1': question.answer1, 'answer2': question.answer2,
                                'num_limit': question.num_limit, 'multi_lines': question.multi_lines,
                                'unit': question.unit})
    return JsonResponse({'errno': 0, 'errmsg': '获取成功', 'qn': qn})


# 点击编辑问卷后返回问卷所有信息
@csrf_exempt
def edit_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_id = body.get("qn_id")
    if qn_id is None:
        return JsonResponse({'errno': 1003, 'errmsg': '问卷id不能为空'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if qn.collection_num != 0:
        return JsonResponse({'errno': 1005, 'errmsg': '问卷已被收集，不可编辑'})
    organization_id = body.get("organization_id")
    if organization_id:
        if not Organization.objects.filter(id=organization_id).exists():
            return  JsonResponse({'errno': 1007, 'errmsg': '组织不存在'})
        organization = Organization.objects.get(id=organization_id)
        if not Organization_2_User.objects.filter(
                organization=organization,user=user).exists():
            return JsonResponse({'errno': 1006, 'errmsg': '用户权限错误'})
        if Organization_2_User.objects.get(organization=organization, user=user).state <= 2:
            return JsonResponse({'errno': 1006, 'errmsg': '用户权限错误'})
    else:
        if not User_create_Questionnaire.objects.filter(user=user, questionnaire=qn).exists():
            return JsonResponse({'errno': 1006, 'errmsg': '用户权限错误'})
    return_qn = qn.info()
    questions = Question.objects.filter(questionnaire=qn).all()
    for question in questions:
        return_qn['questions'].append(question.info())
    return JsonResponse({'errno': 0, 'errmsg': '获取成功', 'qn': return_qn})


@csrf_exempt
def save_qn_file(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    file = body.get("file")
    if file is None:
        return JsonResponse({'errno': 1003, 'errmsg': '文件不能为空'})
    file_name = body.get("file_name")
    if file_name is None:
        return JsonResponse({'errno': 1004, 'errmsg': '文件名不能为空'})
    file_name = urllib.parse.quote(file_name)
    decoded_file = base64.b64decode(file)
    save_path = settings.MEDIA_ROOT + "questionnaire/temp/edit_cache/"
    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, file_name)
    while os.path.exists(file_path):
        file_path = '.' + file_path.split(".")[1] + "_1." + file_path.split(".")[2]
    with open(file_path, 'wb') as f:
        f.write(decoded_file)
    url = file_path
    return JsonResponse({'errno': 0, 'errmsg': '保存成功', 'url': url})


@csrf_exempt
def read_qn_file(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    file_url = body.get("file_url")
    if file_url is None:
        return JsonResponse({'errno': 1003, 'errmsg': '文件路径不能为空'})
    with open(file_url, "rb") as file:
        content = file.read()
    encoded_content = base64.b64encode(content)
    return JsonResponse({'errno': 0, 'errmsg': '读取成功', 'content': encoded_content.decode('utf-8')})


# 保存问卷，若是新建问卷则返回前端无id，若是编辑问卷则返回前端id
@csrf_exempt
def save_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    qn = None
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_id = body.get("qn_id")
    organization_id = body.get("organization_id")
    if organization_id and not Organization.objects.filter(id=organization_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '组织不存在'})
    qn_type = body.get("type")
    if qn_type is None:
        return JsonResponse({'errno': 1004, 'errmsg': '问卷类型不能为空'})
    qn_public = body.get("public")
    if qn_public is None:
        qn_public = True
    qn_permission = body.get("permission")
    if qn_permission is None:
        qn_permission = 0
    qn_collection_num = body.get("collection_num")
    if qn_collection_num is None:
        qn_collection_num = 0
    qn_title = body.get("title")
    if qn_title is None:
        return JsonResponse({'errno': 1005, 'errmsg': '问卷标题不能为空'})
    qn_state = body.get("state")
    if qn_state is None:
        qn_state = 0
    qn_release_time = body.get("release_time")
    if qn_release_time is None:
        qn_release_time = None
    qn_finish_time = body.get("finish_time")
    if qn_finish_time is None:
        qn_finish_time = None
    qn_start_time = body.get("start_time")
    if qn_start_time is None:
        qn_start_time = None
    qn_duration = body.get("duration")
    if qn_duration is None:
        qn_duration = None
    qn_password = body.get("password")
    if qn_password is None:
        qn_password = None
    else:
        qn_public = False
    qn_description = body.get("description")
    if qn_description is None:
        qn_description = None
    qn_background_image = body.get("background_image")
    if not qn_background_image:
        qn_background_image = None
    else:
        try:
            with open(qn_background_image, 'rb') as f:
                file_content = f.read()
                file_name = f.name
            qn_background_image = ContentFile(file_content, file_name)
        except:
            qn_background_image = None
    qn_header_image = body.get("header_image")
    if not qn_header_image:
        qn_header_image = None
    else:
        try:
            with open(qn_header_image, 'rb') as f:
                file_content = f.read()
                file_name = f.name
            qn_header_image = ContentFile(file_content, file_name)
        except:
            qn_header_image = None
    qn_font_color = body.get("font_color")
    if qn_font_color is None:
        qn_font_color = None
    qn_header_font_color = body.get("header_font_color")
    if qn_header_font_color is None:
        qn_header_font_color = None
    qn_question_num_visible = body.get("question_num_visible")
    if qn_question_num_visible is None:
        qn_question_num_visible = True
    if qn_id is None:
        qn = Questionnaire.objects.create(type=qn_type, public=qn_public, permission=qn_permission,
                                          collection_num=qn_collection_num, title=qn_title,
                                          state=qn_state, release_time=qn_release_time,
                                          finish_time=qn_finish_time,
                                          start_time=qn_start_time, duration=qn_duration,
                                          password=qn_password, description=qn_description,
                                          font_color=qn_font_color,
                                          header_font_color=qn_header_font_color,
                                          question_num_visible=qn_question_num_visible)
        qn.background_image = qn_background_image
        qn.header_image = qn_header_image
        qn.save()
    else:
        if not Questionnaire.objects.filter(id=qn_id).exists():
            return JsonResponse({'errno': 1006, 'errmsg': '问卷不存在'})
        qn = Questionnaire.objects.get(id=qn_id)
        qn.type = qn_type
        qn.public = qn_public
        qn.permission = qn_permission
        qn.collection_num = qn_collection_num
        qn.title = qn_title
        qn.state = qn_state
        qn.release_time = qn_release_time
        qn.finish_time = qn_finish_time
        qn.start_time = qn_start_time
        qn.duration = qn_duration
        qn.password = qn_password
        qn.description = qn_description
        qn.background_image = qn_background_image
        qn.header_image = qn_header_image
        qn.font_color = qn_font_color
        qn.header_font_color = qn_header_font_color
        qn.question_num_visible = qn_question_num_visible
        qn.save()
        for question in Question.objects.filter(questionnaire=qn_id).all():
            question.delete()
    # qn_background_image = body.get("background_image")
    # if qn_background_image:
    #     os.remove(qn_background_image)
    # qn_header_image = body.get("header_image")
    # if qn_header_image:
    #     os.remove(qn_header_image)
    questions = body.get("questions")
    for question in questions:
        question_type = question.get("type")
        if question_type is None:
            return JsonResponse({'errno': 1007, 'errmsg': '问题类型不能为空'})
        question_description = question.get("description")
        if question_description is None:
            question_description = None
        question_necessary = question.get("necessary")
        if question_necessary is None:
            question_necessary = False
        question_surface = question.get("surface")
        if question_surface is None:
            question_surface = None
        question_width = question.get("width")
        if question_width is None:
            question_width = 200
        question_order = question.get("order")
        if question_order is None:
            return JsonResponse({'errno': 1008, 'errmsg': '问题序号不能为空'})
        question_change_line = question.get("change_line")
        if question_change_line is None:
            question_change_line = False
        question_score = question.get("score")
        if question_score is None:
            question_score = None
        question_content1 = question.get("content1")
        if question_content1 is None:
            if question_type == 1 or question_type == 2 or question_type == 6:
                return JsonResponse({'errno': 1009, 'errmsg': '问题选项不能为空'})
            question_content1 = None
        question_content2 = question.get("content2")
        if question_content2 is None:
            question_content2 = None
        question_video = question.get("video")
        if not question_video:
            question_video = None
        else:
            try:
                with open(question_video, 'rb') as f:
                    file_content = f.read()
                    file_name = f.name.split('/')[-1]
                    question_video = ContentFile(file_content, file_name)
            except Exception as e:
                print(e)
                question_video = None
        question_image = question.get("image")
        if not question_image:
            question_image = None
        else:
            try:
                with open(question_image, 'rb') as f:
                    file_content = f.read()
                    file_name = f.name.split('/')[-1]
                    question_image = ContentFile(file_content, file_name)
            except:
                question_image = None
        question_answer1 = question.get("answer1")
        if question_answer1 is None:
            question_answer1 = None
        question_answer2 = question.get("answer2")
        if question_answer2 is None:
            question_answer2 = None
        num_limit = question.get("num_limit")
        if num_limit is None:
            num_limit = None
        multi_lines = question.get("multi_lines")
        if multi_lines is None:
            multi_lines = 1
        unit = question.get("unit")
        if unit is None:
            unit = None
        question0 = Question.objects.create(questionnaire=qn, type=question_type,
                                            description=question_description, necessary=question_necessary,
                                            surface=question_surface, width=question_width,
                                            order=question_order,
                                            change_line=question_change_line, score=question_score,
                                            content1=question_content1, content2=question_content2,
                                            answer1=question_answer1, answer2=question_answer2,
                                            num_limit=num_limit, multi_lines=multi_lines, unit=unit)
        question0.video = question_video
        question0.image = question_image
        question0.save()
        # question_video = question.get("video")
        # if question_video:
        #     try:
        #         os.remove(question_video)
        #     except:
        #         pass
        # question_image = question.get("image")
        # if question_image:
        #     try:
        #         os.remove(question_image)
        #     except:
        #         pass
    if qn.type == 1:
        score = 0
        for question in Question.objects.filter(questionnaire=qn).all():
            if question.score:
                score += question.score
        qn.score = score
        qn.save()
    if organization_id is None:
        if not User_create_Questionnaire.objects.filter(questionnaire=qn.id).exists():
            User_create_Questionnaire.objects.create(questionnaire=qn, user=user)
    else:
        if not Organization_create_Questionnaire.objects.filter(questionnaire=qn.id).exists():
            organization = Organization.objects.get(id=organization_id)
            Organization_create_Questionnaire.objects.create(questionnaire=qn,
                                                             organization=organization)
            temp = Organization_2_User.objects.filter(organization=organization,
                                                      user=user).first()
            if temp.state == 2:
                temp.state = 1
                temp.save()
            for temp in Organization_2_User.objects.filter(organization=organization_id).all():
                if temp.state >= 1:
                    Message.objects.create(user=temp.user, message="您所在的组织发布了新的问卷调查，快去看看吧！", type=6)

    return JsonResponse({'errno': 0, 'errmsg': '保存成功', 'qn_id': qn.id})
