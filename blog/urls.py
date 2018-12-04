from django.conf.urls import url

from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^post/new/$', views.new_post, name='new_post'),
    url(r'^post/(?P<pk>\d+)/edit/$', views.edit_post, name='edit_post'),
]
