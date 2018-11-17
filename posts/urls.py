from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^bloglist$', views.bloglist, name="blog"),
    url(r'^success$', views.success_message, name="success"),
    url(r'^create/$', views.post_create),
    url(r'^(?P<slug>[\w-]+)/$', views.article, name= 'article'),
    url(r'^(?P<slug>[\w-]+)/edit/$', views.post_update, name= 'update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', views.post_delete),
]
 