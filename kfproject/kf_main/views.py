from django.shortcuts import render
from django.http import HttpResponse
from kfproject import credentials as cred
from .models import Deck, Card, Deck_Card, Deck_House

def index(request):
    return render(request, 'kf_main/index.html')


def deck_search(request):

    test = Deck.objects.all().count()


    return render(request, 'kf_main/deck_detail.html', {'test': test})