from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from . import credentials as cred 
from .models import Deck, Card, Deck_Card, Deck_House, Deck2
from . import kf_data as kf
from . import kf_data_v2 as kf2
from django.db.models import Sum, Q
from . import deck_processor as dp
from collections import defaultdict 

import json
from django.core import serializers

from django.db import connection
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
    deck_list = Deck2.objects.filter(name__icontains=deck_name)

    if not deck_list:
        return render(request, 'kf_main/index.html', {'message': 'No decks found'})
    elif len(deck_list) == 1:
        return HttpResponseRedirect(reverse('kf_main:deck_detail', args=(deck_list[0].id,)))
    else:
        return HttpResponseRedirect(reverse('kf_main:deck_list') + '?search=' + deck_name)


def deck_detail(request, deck_id):

    # deck = request.GET['id']
    data = kf.get_specific_deck(deck_id)
    deck = Deck2.objects.get(id=deck_id)         # should be get
    power_list, type_nums = get_stats(data[1])
    g_action, g_artifact, g_creature, g_upgrade, g_amber = get_global_dist()
    top_action, top_artifact, top_creature, top_upgrade, top_amber = get_top_dist()

    card_objects = [] 
    for card_id in data[1]:
        card_objects.append(Card.objects.get(id=card_id))
        

    context = {
        'deck': deck,
        'house1': deck.house_list[0],
        'house2': deck.house_list[1],
        'house3': deck.house_list[2],
        'deck_card_list': card_objects,
        'power_list': power_list,
        'type_nums': type_nums,
        'g_action': g_action,
        'g_artifact': g_artifact,
        'g_creature': g_creature,
        'g_upgrade': g_upgrade,
        'g_amber': g_amber,
        'top_action': top_action,
        'top_artifact': top_artifact,
        'top_creature': top_creature,
        'top_upgrade': top_upgrade,
        'top_amber': top_amber,
    }

    return render(request, 'kf_main/deck_detail.html', context)


def get_stats(deck_cards):      # list of card ids
    # _, deck_cards, _ = data
    power_list = {} 
    type_nums = {
        'action': 0,
        'artifact': 0,
        'creature': 0,
        'upgrade': 0
    }
    for card in deck_cards:     
        card_details = Card.objects.get(id=card)        
        type_nums[card_details.card_type.lower()] += 1       
        if card_details.power == 0:
            continue
        elif card_details.power in power_list:
            power_list[card_details.power] += 1
        else:
            power_list[card_details.power] = 1

    type_list = []
    for card_type in type_nums:
        type_list.append({'type': card_type, 'amount': type_nums[card_type]})

    return (power_list, type_list)


def get_global_dist():
    deck_list = Deck.objects.all()
    return (get_dist(deck_list))
            
            
def get_top_dist():
    deck_list = Deck.objects.filter(power_level__gt=1)
    top_decks = []

    for deck in deck_list:
        if deck.losses != 0 and deck.power_level == 2:
            if deck.wins / deck.losses >= 3:
                top_decks.append(deck) 
        else:
            top_decks.append(deck)

    return(get_dist(top_decks))


def get_dist(deck_list):
    action_dist, artifact_dist, creature_dist, upgrade_dist, amber_dist = {}, {}, {}, {}, {} 
    for deck in deck_list:
        if deck.num_action in action_dist:
            action_dist[deck.num_action] += 1
        else:
            action_dist[deck.num_action] = 1
        if deck.num_artifact in artifact_dist:
            artifact_dist[deck.num_artifact] += 1
        else:
            artifact_dist[deck.num_artifact] = 1
        if deck.num_creature in creature_dist:
            creature_dist[deck.num_creature] += 1
        else:
            creature_dist[deck.num_creature] = 1
        if deck.num_upgrade in upgrade_dist:
            upgrade_dist[deck.num_upgrade] += 1
        else:
            upgrade_dist[deck.num_upgrade] = 1
        if deck.bonus_amber in amber_dist:
            amber_dist[deck.bonus_amber] += 1
        else:
            amber_dist[deck.bonus_amber] = 1

    if None in action_dist:
        action_dist.pop(None)
        artifact_dist.pop(None)
        creature_dist.pop(None)
        upgrade_dist.pop(None)
        amber_dist.pop(None)

    return (action_dist, artifact_dist, creature_dist, upgrade_dist, amber_dist)



# Average chains for decks with registered games   
def get_chains():
    total_chains = Deck.objects.aggregate(Sum('chains'))
    deck_count = Deck.objects.filter(Q(wins__gt=0) | Q(losses__gt=0)).count()

    return total_chains['chains__sum']/deck_count


# Average win/loss ratio for decks with registered games 
def get_win_loss():
    deck_list = Deck.objects.filter(Q(wins__gt=0) | Q(losses__gt=0))
    win_loss_total = 0

    for deck in deck_list:
        if deck.losses != 0:
            win_loss_total += deck.wins / deck.losses
        else:
            win_loss_total += deck.wins

    return win_loss_total / len(deck_list)


# Average OP games for decks with registered games
def get_avg_games():
    deck_list = Deck.objects.filter(Q(wins__gt=0) | Q(losses__gt=0))
    total_games = 0

    for deck in deck_list:
        total_games += deck.wins + deck.losses

    return total_games / len(deck_list)



def get_nodes(request):
    # deck_id = request.GET('deck_id')
    data = json.loads(request.body)
    print(data)
    deck_id = data['deck_id']
    print()
    print(deck_id)
    print()
    # cur = connection.cursor()
    # cur.execute('SELECT house FROM deck_house where deck_id = %s', (deck_id,))
    # houses = cur.fetchall()
    user_deck = Deck2.objects.get(id=deck_id)
    houses = user_deck.house_list
    decks = Deck2.objects.all()
    house_match_list = []

    for deck in decks:
        if houses[0] not in deck.house_list or houses[1] not in deck.house_list or houses[2] not in deck.house_list:
            continue
        else:
            house_match_list.append(deck)

    # cur.execute('''
        #     SELECT deck_id from deck_house
        #     where house in (%s, %s, %s)   
        #     group by deck_id                            
        #     having count(distinct house) = 3
        #     ;''', [user_deck.house_list[0], user_deck.house_list[1], user_deck.house_list[2]])
        
        # decks = cur.fetchall()

    percent_match = []
    
    for deck in house_match_list:
        card_count = 0
        for card in user_deck.card_list:
            if card in deck.card_list:
                card_count+=1
        
        percent_match.append([int(card_count/36*100), deck.id, deck.wins, deck.losses])

    percent_match.sort(key=lambda x: x[0], reverse=True)
    percent_match = {'percent_match': percent_match[:26]}

    return JsonResponse(percent_match)





    






# kf2.set_main_data(kf2.page, kf2.site)
# get_nodes('eb5d4c4a-5957-4276-ab9a-0d1b19f42e81')
# get_top_dist()
# dp.set_deck_attrib()
# deck_card_list = Card.objects.filter(deck_card__deck_id=deck)