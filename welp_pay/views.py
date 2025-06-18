from django.shortcuts import render


def home(request):
    """Vista home para Welp Pay"""
    return render(request, 'welp_pay/home.html')


def index(request):
    """Vista index (página principal) para Welp Pay"""
    return render(request, 'welp_pay/index.html') 