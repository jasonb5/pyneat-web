from django import forms
from django.forms.boundfield import BoundField

class FieldSet(object):
    def __init__(self, form, fields, legend):
        self.form = form
        self.fields = fields
        self.legend = legend

    def __iter__(self):
        for name in self.fields:
            yield BoundField(self.form, self.form.fields[name], name)

class ExperimentForm(forms.Form):
    name = forms.CharField()
    generations = forms.IntegerField()
    pop_size = forms.IntegerField()
    coef_matching = forms.DecimalField()
    coef_disjoint = forms.DecimalField()
    compat_threshold = forms.DecimalField()
    survival_rate = forms.DecimalField()
    stagnation_threshold = forms.IntegerField()
    mate_only_prob = forms.DecimalField()
    mutate_only_prob = forms.DecimalField()
    mutate_neuron_prob = forms.DecimalField()
    mutate_gene_prob = forms.DecimalField()
    mutate_power = forms.DecimalField()
    fitness_func = forms.CharField(widget=forms.Textarea)
    num_input = forms.IntegerField()
    num_output = forms.IntegerField()
    runs = forms.IntegerField()
    clamp_weights = forms.DecimalField()
    allow_recurrent = forms.BooleanField(required=False)
