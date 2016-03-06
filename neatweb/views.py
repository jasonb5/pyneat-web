from django.shortcuts import render

def experiments(request):
    return render(request, 'neatweb/experiments.html')
