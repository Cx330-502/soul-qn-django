from django.urls import path
from .views import *

urlpatterns = [
    path('get_examples', get_examples),
    path('create_qn', create_qn),
    path('save_qn', save_qn),
]