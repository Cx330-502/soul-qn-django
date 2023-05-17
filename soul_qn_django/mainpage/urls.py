from django.urls import path
from .views import *

urlpatterns = [
    path('hello/', hello),
    path('listqn/', listqn_views),

    path('generate_link', generate_link),
    path('generate_qrcode', generate_qrcode),
]
