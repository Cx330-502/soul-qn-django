import time

import jwt
from django.conf import settings
from django.db import models


def auth_token(token):
    salt = settings.SECRET_KEY
    try:
        payload = jwt.decode(token, salt, algorithms=['HS256'], verify=True)
        exp_time = payload['exp']
        if time.time() > exp_time:
            raise Exception('Token has expired')
    except Exception as e:
        return False
    if User.objects.filter(id=payload['id']).exists():
        return User.objects.get(id=payload['id'])


class User(models.Model):
    # User表项，含用户名和密码，均为字符串属性，并设置最大长度
    username = models.CharField("用户名", max_length=100)
    password = models.CharField("密码", max_length=20)
    email = models.EmailField("邮箱")

    def create_token(self, timeout):
        salt = settings.SECRET_KEY
        headers = {
            'typ': 'jwt',
            'alg': 'HS256'
        }
        payload = {'id': self.id, 'username': self.username, 'exp': time.time() + timeout}
        token = jwt.encode(payload=payload, key=salt, algorithm='HS256', headers=headers)
        return token


class Organization(models.Model):
    # Organization表项，含组织名和密码，均为字符串属性，并设置最大长度
    name = models.CharField("组织名", max_length=100)


class Questionnaire(models.Model):
    # Questionnaire表项，含问卷名和密码，均为字符串属性，并设置最大长度
    name = models.CharField("问卷名", max_length=100)
    type = models.IntegerField("问卷类型")  #
    collection_num = models.IntegerField("问卷收集人数")
    state = models.IntegerField("问卷状态")
    # 0表示审核中,1表示已发布,-1表示发布失败,2表示尚未开始,-2表示已结束
    release_time = models.DateTimeField("问卷发布时间")
    finish_time = models.DateTimeField("问卷截止时间")
    start_time = models.DateTimeField("问卷开始时间")
    duration = models.IntegerField("问卷持续时间")  # 单位为秒
    password = models.CharField("问卷密码", max_length=20)
    title = models.CharField("问卷标题", max_length=100)
    description = models.CharField("问卷描述", max_length=100)


class Organization_2_User(models.Model):
    # Organization_2_User表项，含组织id和用户id，
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.IntegerField("用户在组织中的状态")
    # 0表示审核中,1表示已通过,-1表示拒绝,2表示可发布一次问卷,3表示可发布多次问卷,4表示可审核且可发布多次问卷


class User_create_Questionnaire(models.Model):
    # User_create_Questionnaire表项，含用户id和问卷id
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    questionnaire_id = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)


class Organization_create_Questionnaire(models.Model):
    # Organization_create_Questionnaire表项，含组织id和问卷id，均为字符串属性，并设置最大长度
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)
    questionnaire_id = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    necessary = models.BooleanField("问卷是否必填")  # True表示必填,False表示非必填


class Question(models.Model):
    # Question表项
    type = models.IntegerField("问题类型")  # 0表示选择,1表示文本
    description = models.CharField("问题描述", max_length=200)
    questionnaire_id = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    necessary = models.BooleanField("问题是否必答")  # True表示必答,False表示非必答
    surface = models.CharField("问题表面", max_length=200)
    width = models.IntegerField("问题宽度")
    order = models.IntegerField("问题顺序")
    change_line = models.IntegerField("问题是否换行")  # 0表示不换行,1表示换行
    score = models.IntegerField("问题分数")


class Choices(models.Model):
    # Choices表项
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, primary_key=True)
    content = models.CharField("选项内容", max_length=400)
    type = models.IntegerField("选项类型")  # 0表示单选,1表示多选
    answer = models.CharField("选项答案", max_length=200)  # 以 "===" 分割


class Texts(models.Model):
    # Texts表项
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, primary_key=True)
    content = models.TextField("文本内容")
    type = models.IntegerField("选项类型")
    answer = models.TextField("文本答案")


class Answer_sheet(models.Model):
    # Answer_sheet表项，含问卷名和密码，均为字符串属性，并设置最大长度
    questionnaire_id = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    answerer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    submit_time = models.DateTimeField("问卷提交时间")
    duration = models.IntegerField("问卷持续时间")  # 单位为秒
    score = models.IntegerField("问卷分数")
    state = models.IntegerField("问卷状态")  # 0表示未完成,1表示已完成,-1表示未提交


class Question_answer(models.Model):
    # Question_answer表项，含问卷名和密码，均为字符串属性，并设置最大长度
    answer_sheet_id = models.ForeignKey(Answer_sheet, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField("回答", max_length=200)
    answer2 = models.TextField("回答2")
    answer3 = models.IntegerField("回答3")
    answer4 = models.ImageField("回答4")
    answer5 = models.FileField("回答5")
    score = models.IntegerField("回答得分")
