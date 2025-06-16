from django.shortcuts import render


def home(request):
    """Vista home para Welp Desk"""
    return render(request, 'welp_desk/home.html') 