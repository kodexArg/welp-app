from django.shortcuts import render


def home(request):
    """Vista home para Welp Pay"""
    return render(request, 'welp_pay/home.html') 