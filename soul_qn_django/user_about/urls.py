from django.urls import path
from .views import *

urlpatterns = [
    path('register/captcha', captcha),
    path('register', register),
    path('login', login),
    path('test_login', test_login),
    path('organization/list_user', organization_list_user),
    path('organization/invite', organization_invite),
    path('organization/pass', organization_pass),
    path('organization/kick', organization_kick),
    path('organization/grant', organization_grant),
    path('organization/search', organization_search),
    path('organization/disband', organization_disband)
]
