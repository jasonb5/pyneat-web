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

def decimal_serializer(o):
    if isinstance(o, decimal.Decimal):
        return str(o)

def organism_query(request):
    org_id = None

    if request.method == 'GET':
        org_id = request.GET['organism_id']

    context = {}

    if org_id:
        organism = models.Organism.objects.get(pk=org_id)

        context['winner'] = organism.winner
        context['fitness'] = organism.fitness
        context['marked'] = organism.marked
        context['rank'] = organism.rank

        network = json.loads(organism.network)

        nodes = { }

        for g in network['genes']:
            if not g['inode'] in nodes:
                nodes[g['inode']] = True

            if not g['onode'] in nodes:
                nodes[g['onode']] = True

        context['nodes'] = nodes.keys()
        context['genes'] = network['genes']
    
    return HttpResponse(json.dumps(context, default=decimal_serializer))

def species_query(request):
    spec_id = None

    if request.method == 'GET':
        spec_id = request.GET['species_id']

    context = {}

    if spec_id:
        species = models.Species.objects.get(pk=spec_id)

        org_count = models.Organism.objects.filter(
                species_id=species.id).count()

        context['org_count'] = org_count
        context['marked'] = species.marked
        context['avg_fitness'] = species.avg_fitness
        context['max_fitness'] = species.max_fitness
        context['offspring'] = species.offspring
        context['age_since_imp'] = species.age_since_imp

    return HttpResponse(json.dumps(context, default=decimal_serializer))

def generation_query(request):
    gen_id = None 

    if request.method == 'GET':
        gen_id = request.GET['generation_id']

    context = {}

    if gen_id:
        generation = models.Generation.objects.get(pk=gen_id)

        winner = models.Organism.objects.filter(
                generation_id=generation.id,
                winner = True)

        context['winner'] = True if winner else False

    return HttpResponse(json.dumps(context, default=decimal_serializer))

def experiment_query(request):
    experiment = None

    if request.method == 'GET':
        exp_id = request.GET['experiment_id']

        if exp_id:
            experiment = get_object_or_404(models.Experiment, pk=exp_id)

    return HttpResponse(experiment.config)

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

        initial['name'] = 'Test'
        initial['fitness_func'] = """def evaluate(net):
        data = ((0.0, 0.0, 1.0),
                (1.0, 0.0, 1.0),
                (0.0, 1.0, 1.0),
                (1.0, 1.0, 1.0))
        result = []
        winner = False

        for d in data:
            result.append(net.activate(d))

        if result[0] < 0.5 and result[1] >= 0.5 and result[2] >= 0.5 and result[3] < 0.5:
            winner = True

        error = math.fabs(result[0]+(1-result[1])+(1-result[2])+result[3])

        fitness = math.pow(4-error, 2)

        return fitness, winner"""

        form = ExperimentForm(initial)

    context = {
            'form': form,
    }

    return render(request, 'neatweb/submission.html', context)

def organisms(request, exp_id, pop_id, gen_id, spec_id):
    org_list = models.Organism.objects.filter(
            population_id=pop_id,
            generation_id=gen_id,
            species_id=spec_id)

    org_ids = dict(map(lambda x: (x.rel_index, x.pk), org_list))

    sel_org = org_list.get(pk=org_ids[0])

    genes = json.loads(sel_org.network)['genes']

    nodes = {}

    for g in genes:
        if not g['inode'] in nodes:
            nodes[g['inode']] = True

        if not g['onode'] in nodes:
            nodes[g['onode']] = True

    context = {
            'org_ids': org_ids,
            'sel_org': sel_org.to_dict(),
            'nodes': nodes.keys(),
            'genes': genes,
    }

    return render(request, 'neatweb/organisms.html', context)

def species(request, exp_id, pop_id, gen_id):
    spec_list = models.Species.objects.filter(
            population_id=pop_id,
            generation_id=gen_id)

    org_count = models.Organism.objects.filter(
            population_id=pop_id,
            generation_id=gen_id,
            species_id=spec_list[0].id).count()

    context = {
            'org_count': org_count,
            'exp_id': exp_id,
            'spec_list': spec_list,
    }

    return render(request, 'neatweb/species.html', context)

def generations(request, exp_id, pop_id):
    gen_list = models.Generation.objects.filter(population_id=pop_id)

    winner = models.Organism.objects.filter(
            population_id=pop_id,
            generation_id=gen_list[0].id,
            winner=True)

    context = {
            'exp_id': exp_id,
            'gen_list': gen_list,
            'winner': winner,
    }

    return render(request, 'neatweb/generations.html', context)

def populations(request, exp_id):
    pop_list = models.Population.objects.filter(experiment_id=exp_id)

    winner = models.Organism.objects.filter(
            population_id=pop_list[0].id,
            winner=True)

    context = {
            'pop_list': pop_list,
            'winner': winner,
    }

    return render(request, 'neatweb/populations.html', context)

def experiments(request):
    exp_list = models.Experiment.objects.all()
    
    context = {
            'exp_list': exp_list,
    }

    return render(request, 'neatweb/experiments.html', context)
