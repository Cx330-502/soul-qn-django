import json
import jieba.analyse
from Qn.models import *
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import xlwt


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
    if qn.type != 2:
        organization_id = body.get('organization_id')
        organization_num = 0
        if organization_id:
            if not Organization.objects.filter(id=organization_id).exists():
                return JsonResponse({'errno': 1004, 'errmsg': '组织编号错误'})
            organization = Organization.objects.get(id=organization_id)
            if not Organization_2_User.objects.filter(user=user, organization=organization).exists():
                return JsonResponse({'errno': 1005, 'errmsg': '无权限'})
            if Organization_2_User.objects.get(user=user, organization=organization).state <= 2:
                return JsonResponse({'errno': 1006, 'errmsg': '权限不足'})
            for temp in Organization_2_User.objects.filter(organization=organization).all():
                if temp.state >= 1:
                    organization_num += 1
        elif not User_create_Questionnaire.objects.filter(user=user, questionnaire=qn).exists():
            return JsonResponse({'errno': 1007, 'errmsg': '无权限'})
    all_info = {'qn': qn.info()}
    for question in qn.question_set.all():
        all_info['qn']['questions'].append(question.info())
        #try:
        extra_data = get_extra_data(question)
        all_info['qn']['questions'][-1]['extra_data'] = extra_data
        # except Exception as e:
        #     print(e)
        #     return JsonResponse({'errno': 1008, 'errmsg': '获取额外数据失败'})
    all_info['answer_sheets'] = []
    for answer_sheet in Answer_sheet.objects.filter(questionnaire=qn).all():
        all_info['answer_sheets'].append(answer_sheet.info())
        for answer in Question_answer.objects.filter(answer_sheet=answer_sheet).all():
            all_info['answer_sheets'][-1]['answers'].append(answer.info())
    return JsonResponse({'errno': 0, 'errmsg': '成功', 'all_info': all_info, 'organization_num': organization_num})


# 更新问卷分数
def update_score(request):
    if request.method != "POST":
        return JsonResponse({'errno': 1001, 'errmsg': '请求方法错误'})
    body = json.loads(request.body)
    token = body.get('token')
    user = auth_token(token)
    if not user:
        return JsonResponse({'errno': 1002, 'errmsg': 'token错误或已过期'})
    answer_sheet_id = body.get('answer_sheet_id')
    if not answer_sheet_id or not Answer_sheet.objects.filter(id=answer_sheet_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '答卷编号错误'})
    answer_sheet = Answer_sheet.objects.get(id=answer_sheet_id)
    question_id = body.get('question_id')
    if not question_id or not Question.objects.filter(id=question_id).exists():
        return JsonResponse({'errno': 1004, 'errmsg': '问题编号错误'})
    question = Question.objects.get(id=question_id)
    new_score = body.get('new_score')
    if not new_score:
        return JsonResponse({'errno': 1005, 'errmsg': '更新分数不能为空'})
    if not Question_answer.objects.filter(answer_sheet=answer_sheet, question=question).exists():
        return JsonResponse({'errno': 1006, 'errmsg': '答卷中无此回答'})
    answer = Question_answer.objects.filter(answer_sheet=answer_sheet, question=question).first()
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
    if qn_id is None or not Questionnaire.objects.filter(id=qn_id).exists():
        return JsonResponse({'errno': 1003, 'errmsg': '问卷编号错误'})
    qn = Questionnaire.objects.get(id=qn_id)
    organization_id = body.get('organization_id')
    if organization_id:
        organization = Organization.objects.filter(id=organization_id).first()
        if not Organization_create_Questionnaire.objects.filter(organization=organization,
                                                                questionnaire=qn).exists():
            return JsonResponse({'errno': 1004, 'errmsg': '无导出权限'})
        if Organization_2_User.objects.get(user=user, organization=organization).state <= 2:
            return JsonResponse({'errno': 1005, 'errmsg': '权限不足'})
    if not User_create_Questionnaire.objects.filter(user=user, questionnaire=qn).exists():
        return JsonResponse({'errno': 1006, 'errmsg': '无导出权限'})
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
        columns += [str(question.order) + str(question.surface)]
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
            row = ['匿名用户', answer_sheet.duration, str(answer_sheet.submit_time)]
        elif qn.permission == 0:
            row = ['匿名用户', answer_sheet.duration, str(answer_sheet.submit_time)]
        else:
            row = [answer_sheet.answerer.username, answer_sheet.duration, str(answer_sheet.submit_time)]
        answer_list = []
        for question in question_list:
            answer = Question_answer.objects.filter(answer_sheet=answer_sheet, question=question).first()
            if answer is not None:
                answer_list.append(answer)
        answer_list.sort(key=lambda x: x.question.order)
        for answer in answer_list:
            if not answer:
                row.append('')
            else:
                if answer.question.type != 3 and answer.question.type != 4:
                    row.append(answer.answer)
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


def get_extra_data(question):
    extra_data = {}
    if question.type == 1 or question.type == 6:
        extra_data['options'] = []
        if question.content1 is None:
            return extra_data
        temp_list = question.content1.split('###')
        for i in range(len(temp_list)):
            extra_data['options'].append({'option': chr(ord('A') + i), 'content': temp_list[i], 'count': 0})
        extra_data['total'] = 0
        extra_data['options'].sort(key=lambda x: x['option'])
        for answer in Question_answer.objects.filter(question=question).all():
            for option in extra_data['options']:
                if answer.answer == option['option']:
                    option['count'] += 1
            extra_data['total'] += 1
        percent = 100
        extra_data['options'].sort(key=lambda x: x['count'], reverse=True)
        for option in extra_data['options']:
            temp = option['count'] / extra_data['total'] * 100
            percent -= temp
            if percent <= 0:
                temp = temp + percent
                percent = 0
            option['percent'] = temp
        if len(extra_data['options']) > 0:
            extra_data['most_option'] = extra_data['options'][0]
            extra_data['least_option'] = extra_data['options'][-1]
        else:
            extra_data['most_option'] = None
            extra_data['least_option'] = None
        extra_data['options'].sort(key=lambda x: x['option'])
    elif question.type == 2:
        extra_data['options'] = []
        if question.content1 is None:
            return extra_data
        temp_list = question.content1.split('###')
        for i in range(len(temp_list)):
            extra_data['options'].append({'option': chr(ord('A') + i), 'content': temp_list[i], 'count': 0})
        extra_data['choices'] = []
        extra_data['total'] = 0
        extra_data['options'].sort(key=lambda x: x['option'])
        for answer in Question_answer.objects.filter(question=question).all():
            for i in range(len(answer.answer)):
                for option in extra_data['options']:
                    if answer.answer[i] == option['option']:
                        option['count'] += 1
            flag = 0
            for choice in extra_data['choices']:
                if answer.answer == choice['choice']:
                    choice['count'] += 1
                    flag = 1
                    break
            if not flag:
                extra_data['choices'].append({'choice': answer.answer, 'count': 1})
            extra_data['total'] += 1
        extra_data['choices'].sort(key=lambda x: x['count'], reverse=True)
        percent = 100
        for choice in extra_data['choices']:
            temp = choice['count'] / extra_data['total'] * 100
            percent -= temp
            if percent <= 0:
                temp = temp + percent
                percent = 0
            choice['percent'] = temp
        extra_data['options'].sort(key=lambda x: x['count'], reverse=True)
        for option in extra_data['options']:
            temp = option['count'] / extra_data['total'] * 100
            option['percent'] = temp
        if len(extra_data['choices']) == 0:
            extra_data['most_choice'] = None
            extra_data['least_choice'] = None
        else:
            extra_data['most_choice'] = extra_data['choices'][0]
            extra_data['least_choice'] = extra_data['choices'][-1]
        if len(extra_data['options']) == 0:
            extra_data['most_option'] = None
            extra_data['least_option'] = None
        else:
            extra_data['most_option'] = extra_data['options'][0]
            extra_data['least_option'] = extra_data['options'][-1]
        extra_data['options'].sort(key=lambda x: x['option'])
        extra_data['choices'].sort(key=lambda x: x['choice'])
    elif question.type == 3:
        extra_data['answers'] = []
        total = 0
        extracted_sentences = ""
        for answer in Question_answer.objects.filter(question=question).all():
            extra_data['answers'].append({'answer': answer.answer2})
            total += 1
            extracted_sentences = extracted_sentences + "     " + answer.answer2
        extra_data['total'] = total
        extra_data['statistics'] = []
        temp = jieba.analyse.extract_tags(extracted_sentences, topK=20, withWeight=True, allowPOS=())
        for tuple0 in temp:
            extra_data['statistics'].append({
                'name': list(tuple0)[0],
                'value': list(tuple0)[1]
            })
    elif question.type == 4:
        extra_data['answers'] = []
        total = 0
        for answer in Question_answer.objects.filter(question=question).all():
            answer = settings.MEDIA_ROOT + answer.answer5.url if answer.answer5 else None
            if answer:
                extra_data['answers'].append({'answer': answer})
                total += 1
        extra_data['total'] = total
    elif question.type == 5 or question.type == 8:
        extra_data['answers'] = []
        total = 0
        for answer in Question_answer.objects.filter(question=question).all():
            answer = answer.answer
            total += 1
            flag = 0
            for answer0 in extra_data['answers']:
                if answer0['answer'] == answer:
                    answer0['count'] += 1
                    flag = 1
                    break
            if not flag:
                extra_data['answers'].append({'answer': answer, 'count': 1})
        extra_data['total'] = total
        extra_data['answers'].sort(key=lambda x: x['count'], reverse=True)
        percent = 100
        for answer in extra_data['answers']:
            temp = answer['count'] / extra_data['total'] * 100
            percent -= temp
            if percent <= 0:
                temp = temp + percent
                percent = 0
            answer['percent'] = temp
        if len(extra_data['answers']) > 0:
            extra_data['most_answer'] = extra_data['answers'][0]
            extra_data['least_answer'] = extra_data['answers'][-1]
        else:
            extra_data['most_answer'] = None
            extra_data['least_answer'] = None
    elif question.type == 7 or question.type == 9:
        extra_data['answers'] = []
        total = 0
        sum = 0
        for answer in Question_answer.objects.filter(question=question).all():
            answer = answer.answer
            total += 1
            sum += float(answer)
            flag = 0
            for answer0 in extra_data['answers']:
                if answer0['answer'] == answer:
                    answer0['count'] += 1
                    flag = 1
                    break
            if not flag:
                extra_data['answers'].append({'answer': answer, 'count': 1})
        extra_data['total'] = total
        extra_data['answers'].sort(key=lambda x: x['count'], reverse=True)
        percent = 100
        for answer in extra_data['answers']:
            temp = answer['count'] / extra_data['total'] * 100
            percent -= temp
            if percent <= 0:
                temp = temp + percent
                percent = 0
            answer['percent'] = temp
        if len(extra_data['answers']) > 0:
            extra_data['most_answer'] = extra_data['answers'][0]
            extra_data['least_answer'] = extra_data['answers'][-1]
        extra_data['average'] = sum / total
    return extra_data
