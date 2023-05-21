from django.urls import path
from .views import *

urlpatterns = [
    path('list_qn/', list_qn),
    path('list_organization/', list_organization),
    path('generate_link', generate_link),
    path('generate_qrcode', generate_qrcode),
    path('qn_about/generate_link', generate_link),
    path('qn_about/generate_qrcode', generate_qrcode),
    path('qn_about/remove_qn', remove_qn),
    path('qn_about/delete_qn', delete_qn),
    path('qn_about/search_qn', search_qn),
    path('qn_about/sort_qn', sort_qn),
    path('qn_about/copy_qn', copy_qn),
    path('qn_about/open_qn', open_qn),
    path('qn_about/close_qn', close_qn),
]
