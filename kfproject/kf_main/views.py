from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from . import credentials as cred 
from .models import Deck, Card, Deck_Card, Deck_House
from . import kf_data as kf

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


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
    power_list, type_nums = get_stats(data[1])

    context = {
        'deck': deck_list[0],
        'deck_card_list': data[1],
        'power_list': power_list,
        'type_nums': type_nums
    }

    return render(request, 'kf_main/deck_detail.html', context)


def get_stats(deck_cards):
    # _, deck_cards, _ = data
    power_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
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


def get_global_stats():
    deck_count = 0
    deck_list = [Deck.objects.get(id='4772f854-d3c8-4c69-89a0-84932b69f121')]
    total_pwr_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    total_type_nums = {
        'action': 0,
        'artifact': 0,
        'creature': 0,
        'upgrade': 0
    }
    avg_type_nums = {}
    con = connect(dbname='keyforge', user=cred.login['user'], host='localhost', password=cred.login['password'])
    

    for deck in deck_list:
        # deck_cards = Card.objects.filter(deck_card__deck_id=deck.id)
        # deck_cards = deck_cards.values_list('id', flat=True)
        cur = con.cursor()
        
        sql = """
            select deck_id from deck_card where deck_id = %s;
        """
        print(deck.id)
        cur.execute(sql, (deck.id, ))
        deck_cards = cur.fetchall()
        print(deck_cards)
        cur.close()
        break #!!!
        power_list, type_nums = get_stats(deck_cards)

        power_list = [power_list[i] + total_pwr_list[i] for i in range(len(power_list))]
        for card_type in type_nums:
            total_type_nums[card_type] += type_nums[card_type]
            deck_count += 1
        
    power_list = [power_list[i]/deck_count for i in range(len(power_list))]
    for card_type in total_type_nums:
        avg_type_nums[card_type] = int(total_type_nums['action']/deck_count)
    
    print(f'avg power: {power_list}')
    print(f'avg card type: {avg_type_nums}')
    




get_global_stats()
# deck_card_list = Card.objects.filter(deck_card__deck_id=deck)