from django.urls import path
from .views import *

urlpatterns = [
    path('right_to_answer', right_to_answer),
    path('save_answers', save_answers),
    path('submit_answers', submit_answers),
]