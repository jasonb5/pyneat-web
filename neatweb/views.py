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

def species(request, exp_id, pop_id, gen_id):
    spec_list = models.Species.objects.filter(
            population_id=pop_id,
            generation_id=gen_id)

    context = {
            'exp_id': exp_id,
            'spec_list': spec_list,
    }

    return render(request, 'neatweb/species.html', context)

def generations(request, exp_id, pop_id):
    gen_list = models.Generation.objects.filter(population_id=pop_id)

    context = {
            'exp_id': exp_id,
            'gen_list': gen_list,
    }

    return render(request, 'neatweb/generations.html', context)

def populations(request, exp_id):
    pop_list = models.Population.objects.filter(experiment_id=exp_id)

    context = {
            'pop_list': pop_list,
    }

    return render(request, 'neatweb/populations.html', context)

def experiments(request):
    exp_list = models.Experiment.objects.all()

    context = {
            'exp_list': exp_list,
            'name': exp_list[0].name,
            'conf': json.loads(exp_list[0].config),
    }

    return render(request, 'neatweb/experiments.html', context)
