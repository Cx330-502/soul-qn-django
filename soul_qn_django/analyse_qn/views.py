import json

from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from Qn.models import *
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import xlwt
import ReportLab


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


# 导出问卷数据
def export_data(request):
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
    if User_create_Questionnaire.objects.filter(user=user, questionnaire=qn).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '无导出权限'})
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('问卷数据')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ["用户名称", "答卷时间", "提交时间"]
    question_list = []
    for question in Question.objects.filter(questionnaire=qn).all():
        question_list.append(question)
    question_list.sort(key=lambda x: x.order)
    for question in question_list:
        columns += [question.order + question.title]
    for col_num in range(len(columns)):
        sheet.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    answer_sheet_list = []
    for answer_sheet in Answer_sheet.objects.filter(questionnaire=qn).all():
        answer_sheet_list.append(answer_sheet)
    answer_sheet_list.sort(key=lambda x: x.submit_time)
    for answer_sheet in answer_sheet_list:
        row_num += 1
        if qn.permission == 2 or qn.permission == 4:
            row = ['匿名用户', answer_sheet.duration, answer_sheet.submit_time]
        elif qn.permission == 0 and answer_sheet.user:
            row = ['匿名用户', answer_sheet.duration, answer_sheet.submit_time]
        else:
            row = [answer_sheet.user.username, answer_sheet.duration, answer_sheet.submit_time]
        answer_list = []
        for question in question_list:
            answer = Question_answer.objects.filter(answer_sheet=answer_sheet, question=question).first()
            answer_list.append(answer)
        answer_list.sort(key=lambda x: x.question.order)
        for answer in answer_list:
            if not answer:
                row.append('')
            else:
                if answer.question.type != 4 and answer.question.type != 5:
                    row.append(answer.answer1)
                if answer.question.type == 3:
                    row.append(answer.answer2)
                if answer.question.type == 4:
                    row.append('文件形式答案无法显示')
        for col_num in range(len(row)):
            sheet.write(row_num, col_num, row[col_num], font_style)
    save_path = os.path.join(settings.MEDIA_ROOT, 'questionnaire/' + str(qn_id) + '/data/')
    os.makedirs(save_path, exist_ok=True)
    file_path = save_path + '问卷数据.xls'
    if os.path.exists(file_path):
        os.remove(file_path)
    wb.save(file_path)
    url = file_path
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'url': url})


# 生成报告
def generate_report(request):
    # if request.method != "POST":
    #     return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    # body = json.loads(request.body)
    # token = body.get('token')
    # user = auth_token(token)
    # if not user:
    #     return JsonResponse({'errno': 1002, 'errmsg': 'token错误或已过期'})
    # qn_id = body.get('qn_id')
    # if not qn_id or not Questionnaire.objects.filter(id=qn_id).exists():
    #     return JsonResponse({'errno': 1003, 'errmsg': '问卷编号错误'})
    # qn = Questionnaire.objects.get(id=qn_id)
    #
    # pdfmetrics.registerFont(TTFont('MiSans', 'file/fonts/MiSans-Regular.ttf'))
    # pdfmetrics.registerFont(TTFont('思源宋体', 'file/fonts/思源宋体.ttf'))
    # pdfmetrics.registerFont(TTFont('方正黑体', 'file/fonts/方正黑体简体.TTF'))
    # doc = SimpleDocTemplate('file/report.pdf', pagesize=A4,
    #                         rightMargin=72, leftMargin=72,
    #                         topMargin=72, bottomMargin=18)
    # contents = [Paragraph(qn.title + "-问卷报告",
    #                       style=ParagraphStyle(name='Normal', fontName='思源宋体', fontSize=20, alignment=TA_CENTER)),
    #             Spacer(doc.width, 30)]
    #
    # # 绘制饼图
    # def DrawPie(question):
    #     pic = Drawing(400, 400)
    #     pic.add(String(0, 160, question.title + "回答情况", fontName='思源宋体', fontSize=16))
    #     pie = Pie()
    #     pie.x = 200
    #     pie.y = 0
    #     answer_list = []
    #     for answer in Question_answer.objects.filter(question=question).all():
    #         flag = False
    #         for answer0 in answer_list:
    #             if answer0.answer == answer.answer1:
    #                 answer0.count += 1
    #                 flag = True
    #                 break
    #         if not flag:
    #             answer_list.append({"answer": answer.answer1, "count": 0})
    #     total = 0
    #     for answer in answer_list:
    #         total += answer["count"]
    #     percent = 100
    #     k = 0
    #     answer_list.sort(key=lambda x: x["count"], reverse=True)
    #     for answer in answer_list:
    #         temp = answer["count"] / total * 100
    #         percent -= temp
    #         if percent <= 0:
    #             temp = temp + percent
    #             percent = 0
    #         pie.data.append(temp)
    #         pie.labels.append(answer["answer"] + " - " + temp + "%" )
    pass
