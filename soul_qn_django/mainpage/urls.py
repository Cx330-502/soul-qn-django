from django.urls import path
from .views import *

urlpatterns = [
    path('hello/', hello),
    path('list_qn/', list_qn),
    path('list_organization/', list_organization),
    path('generate_link', generate_link),
    path('generate_qrcode', generate_qrcode),
]
