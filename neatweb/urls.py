from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.experiments),
    url(r'^experiment/$', views.experiment),
    url(r'^experiment-(?P<exp_id>[0-9]+)/$', views.populations),
]
