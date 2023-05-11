from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Qn.models import *


# Create your views here.
@csrf_exempt
def get_examples(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    token = request.POST.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_type = request.POST.get("type")
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


@csrf_exempt
def create_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    token = request.POST.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    example_id = request.POST.get("example_id")
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
        qn['questions'].append({'type': question.type, 'description': question.description,
                                'necessary': question.necessary, 'surface': question.surface,
                                'width': question.width, 'order': question.order,
                                'change_line': question.change_line, 'score': question.score,
                                'content1': question.content1, 'content2': question.content2,
                                'video': question.video, 'image': question.image,
                                'answer1': question.answer1, 'answer2': question.answer2})
    print(qn)
    print(qn['questions'])
    response = HttpResponse


@csrf_exempt
def save_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    token = request.POST.get("token")
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    qn_title = request.POST.get("title")
    if not qn_title:
        return JsonResponse({'errno': 1003, 'errmsg': '标题不能为空'})
    qn_type = request.POST.get("type")
    if not qn_type:
        return JsonResponse({'errno': 1004, 'errmsg': '类型不能为空'})
    qn_permission = request.POST.get("permission")
