from django.shortcuts import render


def home(request):
    """Vista home para Pay Flow"""
    return render(request, 'pay_flow/home.html')


def index(request):
    """Vista index (página principal) para Pay Flow"""
    return render(request, 'pay_flow/index.html') 