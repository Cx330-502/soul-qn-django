import os
import time

import jwt
import qrcode
from django.conf import settings
from django.core import signing
from django.core.files import File
from django.db import models
from django.conf import settings

qn_url = 'http://127.0.0.1:3306/this_is_a_questionnaire/'


def auth_token(token):
    salt = settings.SECRET_KEY
    try:
        payload = jwt.decode(token, salt, algorithms=['HS256'], verify=True)
        exp_time = payload['exp']
        if time.time() > exp_time:
            raise Exception('Token has expired')
    except Exception as e:
        print(e)
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


# 解密问卷链接
def decode_link(link):
    value = link.split('/')[-1]
    try:
        qn_id = signing.loads(value)
    except signing.BadSignature:
        return False
    return qn_id


def questionnaire_file_upload_to(instance, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'questionnaire/', str(instance.id), '/file/')
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, filename)
    return path


class Questionnaire(models.Model):
    # Questionnaire表项，含问卷名和密码，均为字符串属性，并设置最大长度
    name = models.CharField("问卷名", max_length=100)
    # 问卷类型，0表示普通，1表示考试
    type = models.IntegerField("问卷类型")
    # 问卷是否公开，false表示不公开，true表示公开
    public = models.BooleanField("问卷是否公开", default=True)
    # 问卷权限 0表示不需要登录 1表示需要登录 2表示需要登录但匿名 3表示仅组织内可填写 4表示仅组织内可填写但匿名
    permission = models.IntegerField("问卷权限", default=0)
    collection_num = models.IntegerField("问卷收集人数", default=0)
    state = models.IntegerField("问卷状态", default=0)
    # 0表示审核中,1表示已发布,-1表示发布失败,2表示尚未开始,-2表示已结束
    release_time = models.DateTimeField("问卷发布时间", null=True)
    finish_time = models.DateTimeField("问卷截止时间", null=True)
    start_time = models.DateTimeField("问卷开始时间", null=True)
    duration = models.IntegerField("问卷持续时间", null=True)  # 单位为秒
    password = models.CharField("问卷密码", max_length=20, null=True)
    title = models.CharField("问卷标题", max_length=100)
    description = models.CharField("问卷描述", max_length=100, null=True)
    link = models.CharField("问卷链接", max_length=100, null=True)
    qr_code = models.ImageField("二维码", upload_to=questionnaire_file_upload_to, null=True)

    def info(self):
        return {'id': self.id, 'name': self.name,
                'type': self.type, 'public': self.public,
                'permission': self.permission, 'collection_num': self.collection_num,
                'state': self.state, 'release_time': self.release_time,
                'finish_time': self.finish_time, 'start_time': self.start_time,
                'duration': self.duration, 'password': self.password,
                'title': self.title, 'description': self.description,
                'questions': []}

    # 生成问卷链接
    def generate_link(self):
        value = signing.dumps(self.id)
        return qn_url + value

    def generate_qr_code(self):
        if self.link is None:
            self.link = self.generate_link()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        image_path = 'questionnaire/' + str(self.id) + '/QRcode/' + str(self.id) + '.png'
        img.save(image_path)
        with open(image_path, 'rb') as f:
            self.qr_code = File(f)
            self.save()


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


def question_file_upload_to(instance, filename):
    filename = os.path.basename(filename)
    path = os.path.join(settings.MEDIA_ROOT + 'questionnaire/' + str(instance.questionnaire_id) + '/question/',
                        str(instance.order) + '/')
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, filename)
    return path


class Question(models.Model):
    # Question表项
    # 1表示单选,2表示多选,3表示文本,4表示文件
    # 11表示图片单选,12表示图片多选,13表示图片文本,14表示图片文件
    # 21表示视频单选,22表示视频多选,23表示视频文本,24表示视频文件
    type = models.IntegerField("问题类型")
    description = models.CharField("问题描述", max_length=200, null=True)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    necessary = models.BooleanField("问题是否必答", default=False)  # True表示必答,False表示非必答
    surface = models.CharField("问题表面", max_length=200, null=True)
    width = models.IntegerField("问题宽度")
    order = models.IntegerField("问题顺序")
    change_line = models.IntegerField("问题是否换行")  # 0表示不换行,1表示换行
    score = models.IntegerField("问题分数", null=True)
    content1 = models.CharField("问题内容1", max_length=400, null=True)  # 选择题选项 以 "===" 分割
    content2 = models.TextField("问题内容2", null=True)  # 文本题阅读材料
    video = models.FileField("问题视频", upload_to=question_file_upload_to, null=True, blank=True)
    image = models.ImageField("问题图片", upload_to=question_file_upload_to, null=True, blank=True)
    answer1 = models.CharField("问题答案1", max_length=200, null=True)  # 选择题答案 以 "===" 分割
    answer2 = models.TextField("问题答案2", null=True)  # 文本题答案

    def info(self):
        video = self.video.url if self.video else None
        image = self.image.url if self.image else None
        return {'id': self.id, 'type': self.type,
                'description': self.description, 'questionnaire_id': self.questionnaire_id,
                'necessary': self.necessary, 'surface': self.surface,
                'width': self.width, 'order': self.order,
                'change_line': self.change_line, 'score': self.score,
                'content1': self.content1, 'content2': self.content2,
                'video': video, 'image': image,
                'answer1': self.answer1, 'answer2': self.answer2}


class Answer_sheet(models.Model):
    # Answer_sheet表项，含问卷名和密码，均为字符串属性，并设置最大长度
    questionnaire_id = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    answerer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    submit_time = models.DateTimeField("问卷提交时间", null=True)
    duration = models.IntegerField("问卷持续时间", null=True)  # 单位为秒
    score = models.IntegerField("问卷分数", null=True)
    state = models.IntegerField("问卷状态", null=True)  # 0表示未完成,1表示已完成,-1表示未提交


class Question_answer(models.Model):
    # Question_answer表项，含问卷名和密码，均为字符串属性，并设置最大长度
    answer_sheet_id = models.ForeignKey(Answer_sheet, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField("回答", max_length=200, null=True)
    answer2 = models.TextField("回答2", null=True)
    answer3 = models.IntegerField("回答3", null=True)
    answer4 = models.ImageField("回答4", null=True)
    answer5 = models.FileField("回答5", null=True)
    score = models.IntegerField("回答得分", null=True)
