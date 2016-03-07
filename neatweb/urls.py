from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.experiments),
    url(r'^experiment/$', views.experiment),
]
