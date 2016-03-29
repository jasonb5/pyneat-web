from django.http import HttpResponse
from django.shortcuts import render

from . import models
from .forms import ExperimentForm

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

        context['fitness'] = organism.fitness
        context['marked'] = organism.marked
        context['rank'] = organism.rank
        context['network'] = organism.network
    
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
    exp_id = None

    if request.method == 'GET':
        exp_id = request.GET['experiment_id']

    if exp_id:
        experiment = models.Experiment.objects.get(pk=exp_id)

    # Rebuild json to include name. 
    conf = json.loads(experiment.config)
    conf['name'] = experiment.name

    return HttpResponse(json.dumps(conf))

def organisms(request, exp_id, pop_id, gen_id, spec_id):
    org_list = models.Organism.objects.filter(
            population_id=pop_id,
            generation_id=gen_id,
            species_id=spec_id)

    context = {
            'exp_id': exp_id,
            'org_list': org_list,
            'network': json.loads(org_list[0].network),
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

    exp_form = None

    if exp_list:
        exp_conf = json.loads(exp_list[0].config)
        
        initial = {
            'name': exp_list[0].name,
            'generations': exp_conf['generations'], 
            'population_size': exp_conf['pop_size'],
            'coefficient_matching': exp_conf['coef_matching'],
            'coefficient_disjoint': exp_conf['coef_disjoint'],
            'compatibility_threshold': exp_conf['compat_threshold'],
            'survival_rate': exp_conf['survival_rate'],
            'stagnation_threshold': exp_conf['stagnation_threshold'],
            'mate_only': exp_conf['mate_only_prob'],
            'mutate_only': exp_conf['mutate_only_prob'],
            'mutate_neuron': exp_conf['mutate_neuron_prob'],
            'mutate_gene': exp_conf['mutate_gene_prob'],
            'mutate_power': exp_conf['mutate_power'],
            'fitness_function': exp_conf['fitness_func'],
            'input_nodes': exp_conf['num_input'],
            'output_nodes': exp_conf['num_output'],
            'runs': exp_conf['runs'],
            'allow_recurrent': exp_conf['allow_recurrent'],
        }
    
        exp_form = ExperimentForm(initial)
    
    context = {
            'exp_list': map(lambda x: x.id, exp_list),
            'form': exp_form,
    }

    return render(request, 'neatweb/experiments.html', context)
