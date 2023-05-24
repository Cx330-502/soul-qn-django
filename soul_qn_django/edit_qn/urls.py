from django.urls import path
from .views import *

urlpatterns = [
    path('get_examples', get_examples),
    path('preview_qn', preview_qn),
    path('edit_qn', edit_qn),
    path('save_qn_file', save_qn_file),
    path('save_qn', save_qn),
    path('read_qn_file', read_qn_file),
]
