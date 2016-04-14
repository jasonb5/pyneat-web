from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.experiments),
    url(r'^submission/$', views.submission, name='submission'),
    url(r'^experiment-(?P<exp_id>[0-9]+)/$', views.populations, name='experiment'),
    url(r'^experiment-(?P<exp_id>[0-9]+)/population-(?P<pop_id>[0-9]+)/$',
        views.generations),
    url(r'^experiment-(?P<exp_id>[0-9]+)/population-(?P<pop_id>[0-9]+)/generation-(?P<gen_id>[0-9]+)/$',
        views.species),
    url(r'^experiment-(?P<exp_id>[0-9]+)/population-(?P<pop_id>[0-9]+)/generation-(?P<gen_id>[0-9]+)/species-(?P<spec_id>[0-9]+)/$',
        views.organisms),

    url(r'^experiment/$', views.experiment_query),
    url(r'^generation/$', views.generation_query),
    url(r'^species/$', views.species_query),
    url(r'^organism/$', views.organism_query),
]
