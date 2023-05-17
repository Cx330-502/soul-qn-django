from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello),
    path('listqn/', views.listqn_views),

]
