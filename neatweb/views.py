from django.http import HttpResponse
from django.shortcuts import render

from . import models

import json

def experiment(request):
    exp_id = None

    if request.method == 'GET':
        exp_id = request.GET['experiment_id']

    if exp_id:
        experiment = models.Experiment.objects.get(pk=exp_id)

    # Rebuild json to include name. 
    conf = json.loads(experiment.config)
    conf['name'] = experiment.name

    return HttpResponse(json.dumps(conf))

def experiments(request):
    exp_list = models.Experiment.objects.all()

    context = {
            'exp_list': exp_list,
            'name': exp_list[0].name,
            'conf': json.loads(exp_list[0].config),
    }

    return render(request, 'neatweb/experiments.html', context)
