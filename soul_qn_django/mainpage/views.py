from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
from Qn.models import *


def hello(request):
    return JsonResponse({'message': 'Hello, world!'})


@login_required
def listqn_views(request):
    user = request.user
    userid = user.id
    # 读当前用户创建的问卷
    user_questionnaire = User_create_Questionnaire.objects.filter(user_id=userid)
    context = {'questionnaires': user_questionnaire}
    return render(request, 'listqn.html', context)
