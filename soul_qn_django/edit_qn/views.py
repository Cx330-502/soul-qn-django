import base64
import os

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
    if not qn_type:
        return JsonResponse({'errno': 1003, 'errmsg': '类型不能为空'})
    if not Questionnaire.objects.filter(public=True).filter(type=qn_type).exists():
        return JsonResponse({'errno': 1, 'errmsg': '无同类型问卷'})
    examples = Questionnaire.objects.filter(type=qn_type)[:10]
    examples_list = list(examples)
    for i in range(len(examples_list)):
        examples_list[i] = {"title": examples_list[i].title, "id": examples_list[i].id,
                            "description": examples_list[i].description}
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
    example_id = body.get("example_id")
    if not example_id:
        return JsonResponse({'errno': 1, 'errmsg': '无问卷模板'})
    if not Questionnaire.objects.filter(public=True).filter(id=example_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷模板不存在'})
    example = Questionnaire.objects.get(id=example_id)
    qn = {'title': example.title, 'description': example.description, 'type': example.type,
          'permission': example.permission, 'questions': [],
          'public': example.permission, 'name': example.name}
    questions = Question.objects.filter(questionnaire_id=example).all()
    for question in questions:
        video_data = question.video.url if question.video else None
        image_data = question.image.url if question.image else None
        qn['questions'].append({'type': question.type, 'description': question.description,
                                'necessary': question.necessary, 'surface': question.surface,
                                'width': question.width, 'order': question.order,
                                'change_line': question.change_line, 'score': question.score,
                                'content1': question.content1, 'content2': question.content2,
                                'video': video_data, 'image': image_data,
                                'answer1': question.answer1, 'answer2': question.answer2})
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
    if not qn_id:
        return JsonResponse({'errno': 1003, 'errmsg': '问卷id不能为空'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if qn.collection_num != 0:
        return JsonResponse({'errno': 1005, 'errmsg': '问卷已被收集，不可编辑'})
    return_qn = qn.info()
    questions = Question.objects.filter(questionnaire_id=qn).all()
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
    file_name = body.get("file_name")
    decoded_file = base64.b64decode(file)
    save_path = settings.STATIC_URL+"questionnaire/temp/"
    file_path = os.path.join(save_path, file_name)
    os.makedirs(save_path, exist_ok=True)
    while os.path.exists(file_path):
        file_path = file_path.split(".")[0] + "_1." + file_path.split(".")[1]
    with open(file_path, 'wb') as f:
        f.write(decoded_file)
    url = file_path
    return JsonResponse({'errno': 0, 'errmsg': '保存成功', 'url': url})


# 保存问卷，若是新建问卷则返回前端无id，若是编辑问卷则返回前端id
@csrf_exempt
def save_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_id = body.get("qn_id")
    qn_type = body.get("type")
    if not qn_type:
        return JsonResponse({'errno': 1003, 'errmsg': '类型不能为空'})
    qn_public = body.get("public")
    if not qn_public:
        qn_public = True
    qn_permission = body.get("permission")
    if not qn_permission:
        qn_permission = 0
    qn_collection_num = body.get("collection_num")
    if not qn_collection_num:
        qn_collection_num = 0
    qn_title = body.get("title")
    if not qn_title:
        return JsonResponse({'errno': 1004, 'errmsg': '标题不能为空'})
    qn_state = body.get("state")
    if not qn_state:
        qn_state = 0
    qn_release_time = body.get("release_time")
    if not qn_release_time:
        qn_release_time = None
    qn_finish_time = body.get("finish_time")
    if not qn_finish_time:
        qn_finish_time = None
    qn_start_time = body.get("start_time")
    if not qn_start_time:
        qn_start_time = None
    qn_duration = body.get("duration")
    if not qn_duration:
        qn_duration = None
    qn_password = body.get("password")
    if not qn_password:
        qn_password = None
    qn_description = body.get("description")
    if not qn_description:
        qn_description = None
    if not qn_id:
        qn = Questionnaire.objects.create(type=qn_type, public=qn_public, permission=qn_permission,
                                          collection_num=qn_collection_num, title=qn_title, state=qn_state,
                                          release_time=qn_release_time, finish_time=qn_finish_time,
                                          start_time=qn_start_time, duration=qn_duration, password=qn_password,
                                          description=qn_description)
    else:
        if not Questionnaire.objects.filter(id=qn_id).exists():
            return JsonResponse({'errno': 1005, 'errmsg': '问卷不存在'})
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
        qn.save()
        for question in Question.objects.filter(questionnaire_id=qn_id).all():
            question.delete()
    questions = body.get("questions")
    for question in questions:
        question_type = question.get("type")
        if not question_type:
            return JsonResponse({'errno': 1006, 'errmsg': '问题类型不能为空'})
        question_description = question.get("description")
        if not question_description:
            question_description = None
        question_necessary = question.get("necessary")
        if not question_necessary:
            question_necessary = False
        question_surface = question.get("surface")
        if not question_surface:
            question_surface = None
        question_width = question.get("width")
        if not question_width:
            question_width = None
        question_order = question.get("order")
        if not question_order:
            return JsonResponse({'errno': 1007, 'errmsg': '问题序号不能为空'})
        question_change_line = question.get("change_line")
        if not question_change_line:
            question_change_line = False
        question_score = question.get("score")
        if not question_score:
            question_score = None
        question_content1 = question.get("content1")
        if not question_content1:
            question_content1 = None
        question_content2 = question.get("content2")
        if not question_content2:
            question_content2 = None
        try:
            question_video = request.FILES.get(f'video_{question_order}')
        except:
            question_video = None
        try:
            question_image = request.FILES.get(f'image_{question_order}')
        except:
            question_image = None
        question_answer1 = question.get("answer1")
        if not question_answer1:
            question_answer1 = None
        question_answer2 = question.get("answer2")
        if not question_answer2:
            question_answer2 = None
        question = Question.objects.create(questionnaire_id=qn, type=question_type,
                                           description=question_description, necessary=question_necessary,
                                           surface=question_surface, width=question_width, order=question_order,
                                           change_line=question_change_line, score=question_score,
                                           content1=question_content1, content2=question_content2,
                                           video=question_video, image=question_image,
                                           answer1=question_answer1, answer2=question_answer2)
    return JsonResponse({'errno': 0, 'errmsg': '保存成功', 'qn_id': qn.id})
