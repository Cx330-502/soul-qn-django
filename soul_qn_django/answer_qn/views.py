import base64
import json
import os
from datetime import datetime

from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from Qn.models import *


# /***
#  *      ┌─┐       ┌─┐ + +
#  *   ┌──┘ ┴───────┘ ┴──┐++
#  *   │                 │
#  *   │       ───       │++ + + +
#  *   ███████───███████ │+
#  *   │                 │+
#  *   │       ─┴─       │
#  *   │                 │
#  *   └───┐         ┌───┘
#  *       │         │
#  *       │         │   + +
#  *       │         │
#  *       │         └──────────────┐
#  *       │                        │
#  *       │                        ├─┐
#  *       │                        ┌─┘
#  *       │                        │
#  *       └─┐  ┐  ┌───────┬──┐  ┌──┘  + + + +
#  *         │ ─┤ ─┤       │ ─┤ ─┤
#  *         └──┴──┘       └──┴──┘  + + + +
#  *                神兽保佑
#  *               代码无BUG!
#  */


# Create your views here.
# 回答问卷 主要是检验权限，如果权限没问题则返回问卷所有信息
def answer_qn(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get('token')
    link = body.get('link')
    qn_id = body.get('qn_id')
    if link:
        qn_id = decode_link(link)
    if not qn_id:
        return JsonResponse({'errno': 1002, 'errmsg': '问卷链接错误或无问卷编号'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if qn.state != 1:
        return JsonResponse({'errno': 1004, 'errmsg': '问卷未发布或已关闭'})
    user = None
    answer_sheet = None
    if qn.permission >= 1:
        user = auth_token(token)
        if not user:
            return JsonResponse({'errno': 1005, 'errmsg': 'token错误或已过期'})
        if Answer_sheet.objects.filter(user=user, questionnaire=qn).exists():
            temp = Answer_sheet.objects.get(user=user, questionnaire=qn)
            if temp.state == 1:
                return JsonResponse({'errno': 1006, 'errmsg': '已回答过该问卷'})
            if temp.state == 0:
                answer_sheet = temp.info()
                for answer in Question_answer.objects.filter(answer_sheet=temp, answerer=user).all():
                    answer_sheet['answers'].append(answer.info())
    if qn.permission >= 3:
        if not Organization_create_Questionnaire.objects.filter(questionnaire=qn).exists():
            return JsonResponse({'errno': 1007, 'errmsg': '权限错误'})
        organization = Organization_create_Questionnaire.objects.get(questionnaire=qn).organization
        if not Organization_2_User.objects.filter(organization=organization, user=user).exists():
            return JsonResponse({'errno': 1007, 'errmsg': '权限错误'})
    return_qn = qn.info()
    questions = Question.objects.filter(questionnaire=qn).all()
    for question in questions:
        return_qn['questions'].append(question.info())
    return JsonResponse({'errno': 0, 'errmsg': '权限合法', 'qn': return_qn, 'answer_sheet': answer_sheet})


def save_answers_file(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get('token')
    file = body.get('file')
    if not file:
        return JsonResponse({'errno': 1002, 'errmsg': '文件不存在'})
    file_name = body.get('file_name')
    if not file_name:
        return JsonResponse({'errno': 1003, 'errmsg': '文件名不存在'})
    decoded_file = base64.b64decode(file)
    save_path = os.path.join(settings.MEDIA_ROOT, 'questionnaire/temp/')
    file_path = os.path.join(save_path, file_name)
    os.makedirs(save_path, exist_ok=True)
    while os.path.exists(file_path):
        file_path = file_path.split('.')[0] + '_1.' + file_path.split('.')[1]
    with open(file_path, 'wb') as f:
        f.write(decoded_file)
    url = file_path
    return JsonResponse({'errno': 0, 'errmsg': '文件保存成功', 'url': url})


def save_answers(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get('token')
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误或已过期'})
    qn_id = body.get('qn_id')
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if Answer_sheet.objects.filter(user=user, questionnaire=qn).exists():
        Answer_sheet.objects.filter(user=user, questionnaire=qn).delete()
    duration = body.get('duration')
    answer_sheet = Answer_sheet.objects.create(user=user, questionnaire=qn, duration=duration, state=0)
    answers = body.get('answers')
    for answer in answers:
        question_id = answer.get('question_id')
        if not question_id:
            return JsonResponse({'errno': 1004, 'errmsg': '问题编号错误'})
        if not Question.objects.filter(id=question_id).exists():
            return JsonResponse({'errno': 1005, 'errmsg': '问题不存在'})
        question = Question.objects.get(id=question_id)
        answer1 = answer.get('answer')
        type0 = question.type % 10
        if type0 != 3 and type0 != 4:
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer=answer1)
        elif type0 == 3:
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer2=answer1)
        elif type0 == 4:
            if not answer1:
                answer1 = None
            else:
                try:
                    with open(answer1, 'rb') as f:
                        file_content = f.read()
                        file_name = f.name.split('/')[-1]
                    answer1 = ContentFile(file_content, file_name)
                except Exception as e:
                    print(e)
                    answer1 = None
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer5=answer1)
    return JsonResponse({'errno': 0, 'errmsg': '保存成功'})


def submit_answers(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get('token')
    user = auth_token(token)
    if not user:
        user = None
    qn_id = body.get('qn_id')
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if user is not None:
        if Answer_sheet.objects.filter(user=user, questionnaire=qn).exists():
            Answer_sheet.objects.filter(user=user, questionnaire=qn).delete()
    duration = body.get('duration')
    answers = body.get('answers')
    for answer in answers:
        question_id = answer.get('question_id')
        if not question_id:
            return JsonResponse({'errno': 1004, 'errmsg': '问题编号错误'})
        if not Question.objects.filter(id=question_id).exists():
            return JsonResponse({'errno': 1005, 'errmsg': '问题不存在'})
        question = Question.objects.get(id=question_id)
        answer1 = answer.get('answer')
        if question.necessary and not answer1:
            return JsonResponse({'errno': 1006, 'errmsg': '必填问题未填写'})
    answer_sheet = Answer_sheet.objects.create(user=user, questionnaire=qn, duration=duration, state=1,
                                               submit_time=datetime.now())
    for answer in answers:
        question_id = answer.get('question_id')
        if not question_id:
            return JsonResponse({'errno': 1004, 'errmsg': '问题编号错误'})
        if not Question.objects.filter(id=question_id).exists():
            return JsonResponse({'errno': 1005, 'errmsg': '问题不存在'})
        question = Question.objects.get(id=question_id)
        answer1 = answer.get('answer')
        type0 = question.type % 10
        if type0 == 1 or type0 == 2 or type0 == 5:
            score = None
            if qn.type == 1:
                if type0 == 1 or type0 == 5 or type0 == 6 or type0 == 7 or type0 == 8 or type0 == 9:
                    if question.answer1 != answer1:
                        score = 0
                    else:
                        score = question.score
                elif type0 == 2:
                    answer_list = question.answer2.split('===')
                    answer_list2 = answer1.split('===')
                    for answer2 in answer_list2:
                        if answer2 not in answer_list:
                            score = 0
                            break
                    if score is None:
                        if len(answer_list) != len(answer_list2):
                            score = question.score // 2
                        else:
                            score = question.score
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer=answer1, score=score)
        elif type0 == 3:
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer2=answer1)
        elif type0 == 4:
            if not answer1:
                answer1 = None
            else:
                try:
                    with open(answer1, 'rb') as f:
                        file_content = f.read()
                        file_name = f.name.split('/')[-1]
                    answer1 = ContentFile(file_content, file_name)
                except Exception as e:
                    print(e)
                    answer1 = None
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer5=answer1)
    if qn.type == 1:
        answer_sheet.score = 0
        for answer in Question_answer.objects.filter(answer_sheet=answer_sheet):
            if answer.score is not None:
                answer_sheet.score += answer.score
    qn.collection_num += 1
    qn.save()
    return JsonResponse({'errno': 0, 'errmsg': '保存成功', 'score': answer_sheet.score})
