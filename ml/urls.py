from django.conf.urls import url

from . import views

app_name = 'ml'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^train_model/$', views.train_model, name='train_model'),
]
