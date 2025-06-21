from django.shortcuts import render


def index(request):
    """Vista index (página principal) para Welp Desk"""
    return render(request, 'welp_desk/index.html') 