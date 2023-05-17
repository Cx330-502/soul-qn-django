import json
from Qn.models import *
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
# 获取问卷相关的所有信息
def get_all_info(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get('token')
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误或已过期'})
    qn_id = body.get('qn_id')
    if not qn_id or not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷编号错误'})
    qn = Questionnaire.objects.get(id=qn_id)
    if not User_create_Questionnaire.objects.filter(user=user, questionnaire=qn).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '无权限'})
    all_info = {'qn': qn.info()}
    for question in qn.question_set.all():
        all_info['qn']['questions'].append(question.info())
    all_info['answer_sheets'] = []
    for answer_sheet in Answer_sheet.objects.filter(questionnaire=qn).all():
        all_info['answer_sheets'].append(answer_sheet.info())
        for answer in Question_answer.objects.filter(answer_sheet=answer_sheet).all():
            all_info['answer_sheets'][-1]['answers'].append(answer.info())
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'all_info': all_info})


# 更新问卷分数
def update_score(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get('token')
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误或已过期'})
    qn_id = body.get('qn_id')
    if not qn_id or not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷编号错误'})
    qn = Questionnaire.objects.get(id=qn_id)
    answer_sheet_id = body.get('answer_sheet_id')
    if not answer_sheet_id or not Answer_sheet.objects.filter(id=answer_sheet_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '答卷编号错误'})
    answer_sheet = Answer_sheet.objects.get(id=answer_sheet_id)
    question_id = body.get('question_id')
    if not question_id or not Question.objects.filter(id=question_id).exists():
        return JsonResponse({'errno': 1005, 'errmsg': '问题编号错误'})
    question = Question.objects.get(id=question_id)
    new_score = body.get('new_score')
    if not new_score:
        return JsonResponse({'errno': 1006, 'errmsg': '更新分数不能为空'})
    answer = Question_answer.objects.filter(answer_sheet=answer_sheet, question=question).first()
    if not answer.exists():
        return JsonResponse({'errno': 1007, 'errmsg': '答卷中无此问题'})
    answer.score = new_score
    answer.save()
    answer_sheet.score = 0
    for answer in Question_answer.objects.filter(answer_sheet=answer_sheet):
        if answer.score is not None:
            answer_sheet.score += answer.score
    answer_sheet.save()
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'total_score': answer_sheet.score})

# 生成报告
def generate_report(request):
    pass


# 导出问卷数据
def export_data(request):
    pass
