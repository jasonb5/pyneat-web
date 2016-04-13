from __future__ import unicode_literals

from django.db import models

class Experiment(models.Model):
    name = models.CharField(max_length=64)
    jid = models.CharField(max_length=37)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
    config = models.TextField()

class Population(models.Model):
    rel_index = models.IntegerField()
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

class Generation(models.Model):
    rel_index = models.IntegerField()
    population = models.ForeignKey(Population, on_delete=models.CASCADE)

class Species(models.Model):
    rel_index = models.IntegerField()
    marked = models.BooleanField()
    avg_fitness = models.DecimalField(max_digits=32, decimal_places=24)
    max_fitness = models.DecimalField(max_digits=32, decimal_places=24)
    offspring = models.IntegerField()
    age_since_imp = models.IntegerField()
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)

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
