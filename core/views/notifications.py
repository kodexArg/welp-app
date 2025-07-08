from django.contrib import messages
from django.shortcuts import render


def notifications_view(request):
    """Return global notifications rendered as a component."""
    return render(request, 'components/core/notifications.html')

