from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^question/(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^question/new/$', views.new_question, name='new_question'),
    url(r'^question/(?P<pk>\d+)/edit/$', views.edit_question, name='edit_question'),
    url(r'^question/(?P<pk>\d+)/delete/$', views.delete_question, name='delete_question'),
]