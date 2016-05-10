from __future__ import unicode_literals

from django.db import models
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from django.db.models import ExpressionWrapper
from django.db.models.fields import FloatField

class Experiment(models.Model):
    name = models.CharField(max_length=64)
    jid = models.CharField(max_length=37)
    progress = models.DecimalField(max_digits=5, decimal_places=2)
    message = models.CharField(max_length=256, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
    config = models.TextField()

    def populations(self):
        return Population.objects.filter(experiment=self.pk)

class Population(models.Model):
    rel_index = models.IntegerField()
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    def generations(self):
        return Generation.objects.filter(population=self.pk).order_by('rel_index')

    def winners(self):
        return Organism.objects.filter(population=self.pk, winner=True)

    def generation_fitness(self):
        return Organism.objects.filter(
                population=self.pk).values(
                        'generation__rel_index').annotate(
                                sfitness=ExpressionWrapper(
                                    Sum('fitness')/Count('generation__rel_index'),
                                    output_field=FloatField()),
                                grel_index=F('generation__rel_index'))

    def species_fitness(self):
        return Organism.objects.filter(
                population=self.pk).values(
                        'species__rel_index').annotate(
                                sfitness=ExpressionWrapper(
                                    Sum('fitness')/Count('species__rel_index'),
                                    output_field=FloatField()),
                                srel_index=F('species__rel_index'))
                                    

class Generation(models.Model):
    rel_index = models.IntegerField()
    population = models.ForeignKey(Population, on_delete=models.CASCADE)

    def species(self):
        return Species.objects.filter(generation=self.pk).order_by('rel_index')

    def organism_fitness(self):
        return Organism.objects.filter(
                generation=self.pk).values(
                        'rel_index', 'fitness')

    def species_fitness(self):
        return Organism.objects.select_related(
                'species').filter(
                        generation=self.pk).values(
                            'species').annotate(
                                    sfitness=ExpressionWrapper(
                                        Sum('fitness')/Count('species'),
                                        output_field=FloatField()),
                                    srel_index=F('species__rel_index'))

class Species(models.Model):
    rel_index = models.IntegerField()
    marked = models.BooleanField()
    avg_fitness = models.DecimalField(max_digits=32, decimal_places=24)
    max_fitness = models.DecimalField(max_digits=32, decimal_places=24)
    offspring = models.IntegerField()
    age_since_imp = models.IntegerField()
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)

    def organisms(self):
        return Organism.objects.filter(species=self.pk).order_by('rel_index')

    def organism_fitness(self):
        return Organism.objects.filter(
                species=self.pk).values('rel_index', 'fitness')

    def generation_fitness(self):
        return Species.objects.select_related(
                'generation').filter(
                        population=self.population,
                        rel_index=self.rel_index).values(
                                'generation__rel_index', 'avg_fitness')

    def get_concrete_fields(self, exclude=()):
        return dict([(f.name, f.value_from_object(self)) for f in Species._meta.get_fields() 
                if not (f.is_relation or 
                    f.one_to_one or 
                    f.many_to_one) and not f.name in exclude
                ])

class Organism(models.Model):
    rel_index = models.IntegerField()
    winner = models.BooleanField()
    marked = models.BooleanField()
    network = models.TextField()
    fitness = models.DecimalField(max_digits=32, decimal_places=24)
    rank = models.IntegerField()
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)

    def get_concrete_fields(self, exclude=()):
        return dict([(f.name, f.value_from_object(self)) for f in Organism._meta.get_fields() 
                if not (f.is_relation or 
                    f.one_to_one or 
                    f.many_to_one) and not f.name in exclude
                ])
