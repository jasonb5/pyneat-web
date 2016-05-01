from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from . import models
from .forms import ExperimentForm
from .pyneatwrapper import pyneat_wrapper

from pyneat import Conf

from rq import Queue
from redis import Redis

import json

def submission(request):
    if request.method == 'POST':
        form = ExperimentForm(request.POST)

        if form.is_valid():
            conf = Conf()

            for k, v in form.cleaned_data.items():
                if isinstance(v, decimal.Decimal):
                    conf.__dict__[k] = float(v)
                else:
                    conf.__dict__[k] = v

            q = Queue(connection=Redis(host='redis', port=6379))

            q.enqueue(pyneat_wrapper, conf)
    else:
        conf = Conf()
        initial = {}

        for k, v in conf.__dict__.items():
            initial[k] = v 

        form = ExperimentForm(initial)

    context = {
            'form': form,
    }

    return render(request, 'neatweb/submission.html', context)

def organism(request, org_pk):
    org = get_object_or_404(models.Organism, pk=org_pk)

    valid_fields = org.get_concrete_fields(('id'))
    network = json.loads(valid_fields.pop('network'))

    inodes = [i for i in xrange(network['input'])]
    hnodes = [network['input']+i for i in xrange(network['hidden'])]
    onodes = [1000+i for i in xrange(network['output'])]

    neurons = {
            'input': inodes,
            'hidden': hnodes,
            'output': onodes,
    }
     
    context = {
            'org': org,
            'fields': valid_fields,
            'neurons': neurons,
            'genes': network['genes'],
    }

    return render(request, 'neatweb/organism.html', context)

def species(request, spec_pk):
    spec = get_object_or_404(models.Species, pk=spec_pk)

    context = {
            'spec': spec,
            'fields': spec.get_concrete_fields(('id')),
            'org_list': spec.organisms(),
    }

    return render(request, 'neatweb/species.html', context)

def generation(request, gen_pk):
    gen = get_object_or_404(models.Generation, pk=gen_pk)

    context = {
            'gen': gen,
            'spec_list': gen.species(),
    }

    return render(request, 'neatweb/generation.html', context)

def population(request, pop_pk):
    pop = get_object_or_404(models.Population, pk=pop_pk)

    context = {
            'pop': pop,
            'gen_list': pop.generations(),
    }

    return render(request, 'neatweb/population.html', context)

def experiment(request, exp_pk):
    exp = get_object_or_404(models.Experiment, pk=exp_pk)

    context = {
            'exp': exp,
            'exp_config': json.loads(exp.config),
            'pop_list': exp.populations(),
    }

    return render(request, 'neatweb/experiment.html', context)

def home(request):
    exp_list = models.Experiment.objects.all()

    context = {
            'exp_list': exp_list,
    }

    return render(request, 'neatweb/home.html', context)
