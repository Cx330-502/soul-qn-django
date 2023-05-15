from django.urls import path
from .views import *

urlpatterns = [
    path('generate_link', generate_link),
    path('generate_qrcode', generate_qrcode),
]
