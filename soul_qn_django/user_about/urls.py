from django.urls import path
from .views import *

urlpatterns = [
    path('register/captcha', captcha),
    path('register', register),
    path('login', login),
    path('test_login', test_login),
    path('organization/create_organization', organization_create_organization),
    path('organization/list_user', organization_list_user),
    path('organization/invite', organization_invite),
    path('organization/generate_link', organization_generate_link),
    path('organization/list_unreviewed_list', organization_list_unreviewed_list),
    path('organization/pass', organization_pass),
    path('organization/kick', organization_kick),
    path('organization/grant', organization_grant),
    path('organization/search', organization_search),
    path('organization/disband', organization_disband),
    path('organization/approve_join', organization_approve_join),
    path('organization/quit', organization_quit),
    path('message/list', message_list),
    path('message/delete', message_delete),
]
