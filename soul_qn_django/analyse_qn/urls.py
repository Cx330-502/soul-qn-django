from django.urls import path
from .views import *

urlpatterns = [
    path('get_all_info', get_all_info),
    path('update_score', update_score),
    path('generate_report', generate_report),
    path('export_data', export_data)
]
