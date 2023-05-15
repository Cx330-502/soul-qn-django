from django.urls import path
from .views import *

urlpatterns = [
    path('get_examples', get_examples),
    path('preview_qn', preview_qn),
    path('edit_qn', edit_qn),
    path('save_qn', save_qn),
]
