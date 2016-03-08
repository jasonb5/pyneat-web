from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.experiments),
    url(r'^experiment-(?P<exp_id>[0-9]+)/$', views.populations),
    url(r'^experiment-(?P<exp_id>[0-9]+)/population-(?P<pop_id>[0-9]+)/$',
        views.generations),
    url(r'^experiment-(?P<exp_id>[0-9]+)/population-(?P<pop_id>[0-9]+)/generation-(?P<gen_id>[0-9]+)/$',
        views.species),
    url(r'^experiment-(?P<exp_id>[0-9]+)/population-(?P<pop_id>[0-9]+)/generation-(?P<gen_id>[0-9]+)/species-(?P<spec_id>[0-9]+)/$',
        views.organisms),
    url(r'^experiment/$', views.experiment),
    url(r'^generation/$', views.generation),
]
