from django.http import HttpResponse

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from . import models
from .forms import ExperimentForm
from .forms import FieldSet
from .pyneatwrapper import pyneat_wrapper

from pyneat import Conf

from rq import Queue
from redis import Redis

import json
import math
import decimal
import datetime

def query_simualte_fitness_func(request):
    class FakeNet:
        def __init__(self, data):
            for i in xrange(len(data)):
                if len(data[i]) > 1:
                    data[i] = map(lambda x: float(x), data[i])
                else:
                    data[i] = map(lambda x: float(x), data[i])[0]

            self.idx = 0
            self.test_data = data

        def activate(self, data):
            idx = self.idx
            self.idx += 1

            return self.test_data[idx]

    func = request.GET['func']
    data = json.loads(request.GET['data'])

    ns = { 'math': math }

    exec func in ns

    fitness, winner = ns['evaluate'](FakeNet(data))

    return HttpResponse(json.dumps({ 'winner': winner, 'fitness': fitness }))

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

    fieldsets = (
        FieldSet(form, ('name',), 'General'),
        FieldSet(form, (
            'num_input',
            'num_output',
            'fitness_func'), 'Network'),
        FieldSet(form, (
            'runs', 
            'pop_size', 
            'generations',
            'survival_rate',
            'stagnation_threshold',
            'allow_recurrent'), 'NEAT Parameters'),
        FieldSet(form, (
            'coef_matching', 
            'coef_disjoint', 
            'compat_threshold'), 'Genome Matching Parameters'),
        FieldSet(form, (
            'mate_only_prob', 
            'mutate_only_prob', 
            'mutate_neuron_prob',
            'mutate_gene_prob',
            'mutate_power',
            'clamp_weights'), 'Mutation Parameters')
    )

    context = {
            'form': form,
            'fieldsets': fieldsets,
    }

    return render(request, 'neatweb/submission.html', context)

def organism(request, org_pk):
    org = get_object_or_404(models.Organism, pk=org_pk)

    valid_fields = org.get_concrete_fields(('id'))
    network = json.loads(valid_fields.pop('network'))

    neuron_map = {}

    for gene in network['genes']:
        inode = gene['inode']
        onode = gene['onode']

        if not inode in neuron_map:
            neuron_map[inode] = True

        if not onode in neuron_map:
            neuron_map[onode] = True

    neuron_keys = neuron_map.keys()

    neurons = map(lambda x: neuron_keys.index(x), neuron_keys)

    genes = []

    for gene in network['genes']:
        new_gene = {
            'inode': neuron_keys.index(gene['inode']),
            'onode': neuron_keys.index(gene['onode']),
            'weight': gene['weight'],
            'enabled': gene['enabled'],
        }

        genes.append(new_gene)
     
    context = {
            'org': org,
            'fields': valid_fields,
            'neurons': neurons,
            'genes': genes,
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
    exp_list = models.Experiment.objects.all().order_by('-start')

    context = {
            'exp_list': exp_list,
    }

    return render(request, 'neatweb/home.html', context)
