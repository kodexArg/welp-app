from django.shortcuts import render


def home(request):
    """Vista home para Welp Payflow"""
    return render(request, 'welp_payflow/home.html')


def index(request):
    """Vista index (página principal) para Welp Payflow"""
    return render(request, 'welp_payflow/index.html') 