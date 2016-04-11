from pyneat import Experiment
from pyneat import DataObserver
from pyneat import DataLogger

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyneat_web.settings')
import django
django.setup()

from . import models

import json
import decimal

def default_serializer(o):
    if isinstance(o, decimal.Decimal):
        return str(o)

    return o

class NeatObserver(DataObserver):
    def __init__(self):
        self.exp = None
        self.pop = None

    def experiment(self, name, conf):
        self.exp = models.Experiment(
                name = name,
                config = json.dumps(conf.__dict__, default=default_serializer))

        self.exp.save()

    def population(self, pop_index):
        self.pop = models.Population(
                rel_index = pop_index,
                experiment = self.exp)

        self.pop.save()

    def generation(self, gen_index, species):
        gen = models.Generation(
                rel_index = gen_index,
                population = self.pop)

        gen.save()

        organisms = []

        for s in species:
            spec = models.Species(
                    rel_index = s.species_id,
                    marked = s.marked,
                    avg_fitness = s.avg_fitness,
                    max_fitness = s.max_fitness,
                    offspring = s.offspring,
                    age_since_imp = s.age_since_imp,
                    population = self.pop,
                    generation = gen)

            spec.save()

            for o in s.organisms:
                network = {
                    'input': o.genome.neurons[0],
                    'hidden': o.genome.neurons[1],
                    'output': o.genome.neurons[2],
                }

                genes = []

                for g in o.genome.genes:
                    gene = {
                        'inode': g.inode,
                        'onode': g.onode,
                        'weight': g.weight,
                        'enabled': g.enabled,
                    }

                    genes.append(gene)

                network['genes'] = genes

                org = models.Organism(
                        rel_index = o.genome.genome_id,
                        winner = o.winner,
                        marked = o.marked,
                        network = json.dumps(network),
                        fitness = o.fitness,
                        rank = o.rank,
                        species = spec,
                        population = self.pop,
                        generation = gen)

                organisms.append(org)

        models.Organism.objects.bulk_create(organisms)

def pyneat_wrapper(conf):
    logger = DataLogger()
    logger.add_observer(NeatObserver())

    exp = Experiment()

    exp.run(conf.name, conf, logger)
