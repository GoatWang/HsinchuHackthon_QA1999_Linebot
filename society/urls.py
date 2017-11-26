from django.conf.urls import url

from . import views

urlpatterns = [
    url('^index/', views.index),
    url('^callback/', views.callback),
    # url(r'^webcallback/(?P<query>.+)/$', views.webcallback),
    url(r'^webcallback/(?P<query>.+)/$', views.webcallback),
]