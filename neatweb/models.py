from __future__ import unicode_literals

from django.db import models

class Experiment(models.Model):
    name = models.CharField(max_length=64)
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
    avg_fitness = models.DecimalField(max_digits=20, decimal_places=16)
    max_fitness = models.DecimalField(max_digits=20, decimal_places=16)
    offspring = models.IntegerField()
    age_since_imp = models.IntegerField()
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)

class Organism(models.Model):
    rel_index = models.IntegerField()
    winner = models.BooleanField()
    marked = models.BooleanField()
    network = models.CharField(max_length=256)
    fitness = models.DecimalField(max_digits=20, decimal_places=16)
    rank = models.IntegerField()
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
