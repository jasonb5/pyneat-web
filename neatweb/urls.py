from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^experiment/(?P<exp_pk>\d+)/$', views.experiment, name='experiment'),
    url(r'^experiment/(?P<exp_pk>\d+)/delete/$', views.experiment_delete, name='experiment-delete'),
    url(r'^population/(?P<pop_pk>\d+)/$', views.population, name='population'),
    url(r'^generation/(?P<gen_pk>\d+)/$', views.generation, name='generation'),
    url(r'^species/(?P<spec_pk>\d+)/$', views.species, name='species'),
    url(r'^organism/(?P<org_pk>\d+)/$', views.organism, name='organism'),

    url(r'^submission/$', views.submission, name='submission'),

    url(r'^progress/$', views.query_progress, name='progress'),
    url(r'^simulate/fitness/$', views.query_simualte_fitness_func, name='sim_fitness'),
    url(r'^graphs/$', views.query_graphs, name='graphs'),
    url(r'^network/(?P<org_pk>\d+)/$', views.query_network, name='network'),
]
