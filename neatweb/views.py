from django.http import HttpResponse
from django.shortcuts import render

from . import models

def experiment(request):
    exp_id = None

    if request.method == 'GET':
        exp_id = request.GET['experiment_id']

    if exp_id:
        experiment = models.Experiment.objects.get(pk=exp_id)

    return HttpResponse(experiment.config)

def experiments(request):
    exp_list = models.Experiment.objects.all()

    context = {
            'exp_list': exp_list,
    }

    return render(request, 'neatweb/experiments.html', context)
