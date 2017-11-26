from django.conf.urls import url

from . import views

urlpatterns = [
    url('^/', views.index),
    url('^callback/', views.callback),
]