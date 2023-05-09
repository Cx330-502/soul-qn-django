"""soul_qn_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/analyse_qn/", include(('analyse_qn.urls', 'analyse_qn'))),
    path("api/answer_qn/", include(('answer_qn.urls', 'answer_qn'))),
    path("api/edit_qn/", include(('edit_qn.urls', 'edit_qn'))),
    path("api/mainpage/", include(('mainpage.urls', 'mainpage'))),
    path("api/user_about/", include(('user_about.urls', 'user_about'))),
    path("api/Qn/", include(('Qn.urls', 'Qn'))),
]
