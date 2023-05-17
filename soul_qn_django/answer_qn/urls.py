from django.urls import path
from .views import *

urlpatterns = [
    path('answer_qn', answer_qn),
    path('save_answers_file', save_answers_file),
    path('save_answers', save_answers),
    path('submit_answers', submit_answers),
]