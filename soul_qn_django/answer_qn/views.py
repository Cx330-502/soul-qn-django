import base64
import json
import os
from datetime import datetime
import urllib.parse
from django.core.files.base import ContentFile
from django.http import JsonResponse
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
    password = body.get('password')
    if link is not None:
        qn_id = decode_qn_link(link)
    if qn_id is None:
        return JsonResponse({'errno': 1002, 'errmsg': '问卷链接错误或无问卷编号'})
    if not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷不存在'})
    qn = Questionnaire.objects.get(id=qn_id)
    if qn.state != 1:
        return JsonResponse({'errno': 1004, 'errmsg': '问卷未发布或已关闭'})
    if qn.start_time is not None:
        start_time = datetime.combine(qn.start_time, datetime.min.time())
        if start_time > datetime.now():
            return JsonResponse({'errno': 1008, 'errmsg': '问卷未开始'})
    if qn.finish_time is not None:
        finish_time = datetime.combine(qn.finish_time, datetime.min.time())
        if finish_time < datetime.now():
            return JsonResponse({'errno': 1009, 'errmsg': '问卷已结束'})
    user = None
    answer_sheet = None
    if qn.permission >= 1:
        user = auth_token(token)
        if not user:
            return JsonResponse({'errno': 1005, 'errmsg': 'token错误或已过期'})
    if qn.permission >= 3:
        if not Organization_create_Questionnaire.objects.filter(questionnaire=qn).exists():
            return JsonResponse({'errno': 1007, 'errmsg': '权限错误'})
        organization = Organization_create_Questionnaire.objects.get(questionnaire=qn).organization
        if not Organization_2_User.objects.filter(organization=organization, answerer=user).exists():
            return JsonResponse({'errno': 1007, 'errmsg': '权限错误'})
    if qn.password is not None and password is None:
        return JsonResponse({'errno': 1010, 'errmsg': '请输入密码'})
    if qn.password is not None and password is not None and qn.password != password:
        return JsonResponse({'errno': 1011, 'errmsg': '密码错误'})
    return_qn = qn.info()
    questions = Question.objects.filter(questionnaire=qn).all()
    for question in questions:
        return_qn['questions'].append(question.info2())
    user = auth_token(token)
    if user is not None:
        if Answer_sheet.objects.filter(answerer=user, questionnaire=qn).exists():
            temp = Answer_sheet.objects.get(answerer=user, questionnaire=qn)
            if temp.state == 1:
                return JsonResponse({'errno': 1006, 'errmsg': '已回答过该问卷'})
            if temp.state == 0:
                answer_sheet = temp.info()
                for answer in Question_answer.objects.filter(answer_sheet=temp).all():
                    answer_sheet['answers'].append(answer.info())
    return JsonResponse({'errno': 0, 'errmsg': '权限合法', 'qn': return_qn, 'answer_sheet': answer_sheet})


def save_answers_file(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get('token')
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误'})
    file = body.get('file')
    if file is None:
        return JsonResponse({'errno': 1003, 'errmsg': '文件不存在'})
    file_name = body.get('file_name')
    if file_name is None:
        return JsonResponse({'errno': 1004, 'errmsg': '文件名不存在'})
    file_name = urllib.parse.quote(file_name)
    decoded_file = base64.b64decode(file)
    save_path = os.path.join(settings.MEDIA_ROOT, 'questionnaire/temp/answer_cache/')
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
    if Answer_sheet.objects.filter(answerer=user, questionnaire=qn).exists():
        Answer_sheet.objects.filter(answerer=user, questionnaire=qn).delete()
    duration = body.get('duration')
    answer_sheet = Answer_sheet.objects.create(answerer=user, questionnaire=qn, duration=duration, state=0)
    answers = body.get('answers')
    if answers is None:
        return JsonResponse({'errno': 1004, 'errmsg': '答案不存在'})
    for answer in answers:
        question_id = answer.get('question_id')
        if question_id is None:
            return JsonResponse({'errno': 1005, 'errmsg': '问题编号错误'})
        if not Question.objects.filter(id=question_id).exists():
            return JsonResponse({'errno': 1006, 'errmsg': '问题不存在'})
        question = Question.objects.get(id=question_id)
        answer1 = answer.get('answer')
        type0 = question.type % 10
        if type0 != 3 and type0 != 4:
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer=answer1)
        elif type0 == 3:
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer2=answer1)
        elif type0 == 4:
            if answer1 is None:
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
            answer1 = answer.get('answer')
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
        if Answer_sheet.objects.filter(answerer=user, questionnaire=qn).exists():
            Answer_sheet.objects.filter(answerer=user, questionnaire=qn).delete()
    duration = body.get('duration')
    if qn.type == 3:
        if qn.questionnaire_total_num >= qn.collection_num:
            return JsonResponse({'errno': 1007, 'errmsg': '问卷已达到收集上限'}) 
    answers = body.get('answers')
    for answer in answers:
        question_id = answer.get('question_id')
        if question_id is None:
            return JsonResponse({'errno': 1004, 'errmsg': '问题编号错误'})
        if not Question.objects.filter(id=question_id).exists():
            return JsonResponse({'errno': 1005, 'errmsg': '问题不存在'})
        question = Question.objects.get(id=question_id)
        answer1 = answer.get('answer')
        if question.necessary and not answer1:
            return JsonResponse({'errno': 1006, 'errmsg': '必填问题未填写'})
    answer_sheet = Answer_sheet.objects.create(answerer=user, questionnaire=qn, duration=duration, state=1,
                                               submit_time=datetime.now())
    for answer in answers:
        question_id = answer.get('question_id')
        if question_id is None:
            return JsonResponse({'errno': 1004, 'errmsg': '问题编号错误'})
        if not Question.objects.filter(id=question_id).exists():
            return JsonResponse({'errno': 1005, 'errmsg': '问题不存在'})
        question = Question.objects.get(id=question_id)
        answer1 = answer.get('answer')
        type0 = question.type % 10
        if type0 == 1 or type0 == 2 or type0 == 5 or type0 == 6 or type0 == 7 or type0 == 8 or type0 == 9:
            score = None
            if qn.type == 1:
                if type0 == 1 or type0 == 5 or type0 == 6 or type0 == 7 or type0 == 8 or type0 == 9:
                    if question.answer1 != answer1:
                        score = 0
                    else:
                        score = question.score
                elif type0 == 2:
                    answer_list = list(question.answer1)
                    answer_list2 = list(answer1)
                    for answer2 in answer_list2:
                        if answer2 not in answer_list:
                            score = 0
                            break
                    if len(answer_list) == 0 :
                        score = 0
                    if score is None:
                        if len(answer_list) != len(answer_list2):
                            score = question.score // 2
                        else:
                            score = question.score
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question,
                                           answer=answer1, score=score)
        elif type0 == 3:
            Question_answer.objects.create(answer_sheet=answer_sheet, question=question, answer2=answer1)
        elif type0 == 4:
            if answer1 is None:
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
            answer1 = answer.get('answer')
    if qn.type == 1:
        answer_sheet.score = 0
        for answer in Question_answer.objects.filter(answer_sheet=answer_sheet):
            if answer.score is not None:
                answer_sheet.score += answer.score
    qn.collection_num += 1
    qn.save()
    answer_sheet.save()

    return JsonResponse({'errno': 0, 'errmsg': '保存成功', 'score': answer_sheet.score})
