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
import decimal
import datetime

def default_serializer(o):
    if isinstance(o, decimal.Decimal):
        return str(o)
    elif isinstance(o, datetime.datetime):
        return o.strftime('%B %d, %Y, %I:%M %p') 

    return None

def query_progress(request):
    data = models.Experiment.objects.all().values(
            'jid', 'progress', 'message', 'end')

    return HttpResponse(json.dumps(list(data), default=default_serializer))

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

    level = 0
    inodes = [(i, level) for i in xrange(network['input'])]

    # Adds some psuedo level separation, TODO level needs to 
    # be dependent on links coming in.
    hnodes = []
    for i in xrange(network['hidden']):
        idx = network['input']+i
        if idx % network['input'] == 0:
            level += 1

        hnodes.append((idx, level))

    level += 1
    onodes = [(1000+i, level) for i in xrange(network['output'])]

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
            'org_fitness': spec.organism_fitness(),
            'gen_fitness': spec.generation_fitness(),
    }

    return render(request, 'neatweb/species.html', context)

def generation(request, gen_pk):
    gen = get_object_or_404(models.Generation, pk=gen_pk)

    context = {
            'gen': gen,
            'spec_list': gen.species(),
            'org_fitness': gen.organism_fitness(),
            'spec_fitness': gen.species_fitness(),
    }

    return render(request, 'neatweb/generation.html', context)

def population(request, pop_pk):
    pop = get_object_or_404(models.Population, pk=pop_pk)

    context = {
            'pop': pop,
            'gen_list': pop.generations(),
            'gen_fitness': pop.generation_fitness(),
            'spec_fitness': pop.species_fitness(),
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
