from django.http import HttpResponse

from django.shortcuts import render
from django.shortcuts import redirect
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

def query_network(request, org_pk):
    org = models.Organism.objects.get(pk=org_pk)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=network.json'
    response.write(org.network)

    return response

def avg_fitness_by_gen(pop_id):
    population = models.Population.objects.get(pk=pop_id)

    data = population.generation_fitness()

    return { 
            'type': 'bar', 
            'data': list(data),
            'title': 'Average Fitness By Generation',
            'xtitle': 'Generation',
            'ytitle': 'Average Fitness',
    }

def avg_fitness_by_spec(pop_id):
    population = models.Population.objects.get(pk=pop_id)

    data = population.species_fitness()

    return { 
            'type': 'bar', 
            'data': list(data),
            'title': 'Average Fitness By Species',
            'xtitle': 'Species',
            'ytitle': 'Average Fitness',
    }

def organism_fitness(gen_id):
    generation = models.Generation.objects.get(pk=gen_id)

    data = generation.organism_fitness()

    return {
            'type': 'bar',
            'data': list(data),
            'title': 'Organism Fitness',
            'xtitle': 'Organism',
            'ytitle': 'Fitness',
    }

def avg_fitness_by_spec_at_gen(gen_id):
    generation = models.Generation.objects.get(pk=gen_id)

    data = generation.species_fitness()

    return {
            'type': 'bar',
            'data': list(data),
            'title': 'Average Fitness By Species',
            'xtitle': 'Species',
            'ytitle': 'Average Fitness',
    }

def organism_fitness_spec(spec_id):
    species = models.Species.objects.get(pk=spec_id)

    data = species.organism_fitness()

    return {
            'type': 'bar',
            'data': list(data),
            'title': 'Organism Fitness',
            'xtitle': 'Organism',
            'ytitle': 'Fitness',
    }

def avg_fitness_by_gen_at_spec(spec_id):
    species = models.Species.objects.get(pk=spec_id)

    data = species.generation_fitness()

    return {
            'type': 'bar',
            'data': list(data),
            'title': 'Average Fitness By Generation',
            'xtitle': 'Generation',
            'ytitle': 'Average Fitness',
    }

def query_graphs(request):
    data_id = request.GET['id']
    type_id = request.GET['type']

    funcs = {
        '1': avg_fitness_by_gen,
        '2': avg_fitness_by_spec,
        '3': organism_fitness,
        '4': avg_fitness_by_spec_at_gen,
        '5': organism_fitness_spec,
        '6': avg_fitness_by_gen_at_spec,
    }

    data = funcs[type_id](data_id)

    return HttpResponse(json.dumps(data, default=default_serializer));

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

    fieldsets = create_fieldsets(form) 

    context = {
            'form': form,
            'fieldsets': fieldsets,
    }

    return render(request, 'neatweb/submission.html', context)

def create_fieldsets(form):
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

    return fieldsets

def organism(request, org_pk):
    org = get_object_or_404(models.Organism, pk=org_pk)

    valid_fields = org.get_concrete_fields(('id'))
    network = json.loads(valid_fields.pop('network'))

    nodes = {}
    links = []
    group = 0
    names = ['Input', 'Hidden', 'Output']
    offset = [0, network['input'], 1000]

    for i in zip(offset, [network['input'], network['hidden'], network['output']]):
        for j in xrange(i[1]):
            nodes[i[0]+j] = { 'label': names[group] + str(i[0]+j), 'group': group } 
        group += 1

    for g in network['genes']:
        link = {
            'source': nodes.keys().index(g['inode']),
            'target': nodes.keys().index(g['onode']),
            'weight': g['weight'],
            'enabled': g['enabled'],
        }

        links.append(link)

    nodes = map(lambda x: { 'name': nodes.keys().index(x[0]), 'group': x[1]['group'], 'label': x[1]['label'] }, nodes.items())
     
    context = {
            'org': org,
            'fields': valid_fields,
            'nodes': json.dumps(nodes),
            'links': json.dumps(links),
    }

    return render(request, 'neatweb/organism.html', context)

def species(request, spec_pk):
    spec = get_object_or_404(models.Species, pk=spec_pk)

    graphs = [
            { 'name': 'Organism Fitness', 'type': 5 },
            { 'name': 'Average Fitness By Generation', 'type': 6 },
    ]

    context = {
            'spec': spec,
            'fields': spec.get_concrete_fields(('id')),
            'org_list': spec.organisms(),
            'graphs': graphs,
    }

    return render(request, 'neatweb/species.html', context)

def generation(request, gen_pk):
    gen = get_object_or_404(models.Generation, pk=gen_pk)

    graphs = [
            { 'name': 'Organism Fitness', 'type': 3 },
            { 'name': 'Average Fitness By Species', 'type': 4 },
    ]

    context = {
            'gen': gen,
            'spec_list': gen.species(),
            'graphs': graphs,
    }

    return render(request, 'neatweb/generation.html', context)

def population(request, pop_pk):
    pop = get_object_or_404(models.Population, pk=pop_pk)

    graphs = [
            { 'name': 'Average Fitness By Generation', 'type': 1 },
            { 'name': 'Average Fitness By Species', 'type': 2 },
    ]

    context = {
            'pop': pop,
            'gen_list': pop.generations(),
            'graphs': graphs,
    }

    return render(request, 'neatweb/population.html', context)

def experiment_delete(request, exp_pk):
    exp = get_object_or_404(models.Experiment, pk=exp_pk)

    exp.delete()

    return redirect('home')

def experiment(request, exp_pk):
    exp = get_object_or_404(models.Experiment, pk=exp_pk)

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
        config = json.loads(exp.config)

        conf = Conf(**config)
        initial = {}

        for k, v in conf.__dict__.items():
            initial[k] = v 

        form = ExperimentForm(initial)

    context = {
            'exp': exp,
            'exp_config': json.loads(exp.config),
            'pop_list': exp.populations(),
            'form': form,
            'fieldsets': create_fieldsets(form),
    }

    return render(request, 'neatweb/experiment.html', context)

def home(request):
    exp_list = models.Experiment.objects.all().order_by('-start')

    context = {
            'exp_list': exp_list,
    }

    return render(request, 'neatweb/home.html', context)
