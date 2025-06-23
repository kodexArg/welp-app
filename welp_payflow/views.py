from django.shortcuts import render


def home(request):
    return render(request, 'welp_payflow/home.html')


def index(request):
    return render(request, 'welp_payflow/index.html') 