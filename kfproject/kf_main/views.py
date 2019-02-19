from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from kfproject import credentials as cred
from .models import Deck, Card, Deck_Card, Deck_House
from . import kf_data as kf

def index(request):
    return render(request, 'kf_main/index.html')


def deck_list(request):
    deck_name = request.GET['search']
    deck_list = Deck.objects.filter(name__icontains=deck_name)

    return render(request, 'kf_main/deck_list.html', {'deck_list': deck_list})


def deck_search(request):

    deck_name = request.POST['search_string']
    deck_list = Deck.objects.filter(name__icontains=deck_name)

    if not deck_list:
        return render(request, 'kf_main/index.html', {'message': 'No decks found'})
    elif len(deck_list) == 1:
        return HttpResponseRedirect(reverse('kf_main:deck_detail', args=(deck_list[0].id,)))
    else:
        return HttpResponseRedirect(reverse('kf_main:deck_list') + '?search=' + deck_name)


def deck_detail(request, deck_id):

    # deck = request.GET['id']
    data = kf.get_specific_deck(deck_id)
    deck_list = Deck.objects.filter(id=deck_id)
    power_list, type_nums = get_stats(data)

    context = {
        'deck': deck_list[0],
        'deck_card_list': data[1],
        'power_list': power_list,
        'type_nums': type_nums
    }

    return render(request, 'kf_main/deck_detail.html', context)


def get_stats(data):
    _, deck_cards, cards = data
    power_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    type_nums = {
        'action': 0,
        'artifact': 0,
        'creature': 0,
        'upgrade': 0
    }
    for card in deck_cards:     # card is the card id here
        card_details = Card.objects.get(id=card)        
        type_nums[card_details.card_type.lower()] += 1       
        if card_details.power >= 1:
            power_list[card_details.power] += 1
    
    return (power_list, type_nums)





# deck_card_list = Card.objects.filter(deck_card__deck_id=deck)