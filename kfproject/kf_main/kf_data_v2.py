import requests
import re
import json
import time
from time import sleep
import datetime
import ast
from psycopg2 import connect
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

from .models import Deck, Card, Deck_Card, Deck_House, Current_Page, Deck2



program_start_time = time.time()

logging.basicConfig(filename='error.log', filemode = 'a', level=logging.WARNING)
page = '1' 
site = ('https://www.keyforgegame.com/api/decks/?page=','&page_size=25&links=cards&ordering=date') 


def get_num_pages():
    response = requests.get(site[0] + page + site[1]).json()
    count = int(response['count'])
    pages = count // 25
    return pages


def set_main_data(page, site):
    data = {} 
    cards = []
    decks = []
    page_count = 0
    deck_objs = []
    card_objs = []

    pages = get_num_pages()
    try:
        page = Current_Page.objects.all()
        page = page[0].page
    except IndexError:
        page = 1
    finally:
        if page == pages:
            page = 1
    
    for i in range(0, pages-page + 1): 
        url = site[0] + str(page) + site[1]
        start_time = time.time()
        card_list = []
        deck_list = []
        house_list = []
        deck_card_list = []
        card_dict = {}

        try:
            cards, decks = assign_data(url)
        except:
            print('Error timeout. Sleeeeeep')
            sleep(5)
            print('Reattempting data retrieval')

            try:
                cards, decks = assign_data(url)
                print('Data collection successful.')
            except:
                logging.exception(f'{datetime.datetime.now()} Error retrieving data on page: {page}')

            continue


        for card in cards:
            card_dict[card['id']] = card

            new_card = Card(
                id = card['id'],
                card_title = card['card_title'],
                house = card['house'],
                card_type = card['card_type'],
                front_image = card['front_image'],
                card_text = card['card_text'],
                traits = card['traits'],
                amber = card['amber'],
                power = card['power'],
                armor = card['armor'],
                rarity = card['rarity'],
                flavor_text = card['flavor_text'],
                card_number = card['card_number'],
                expansion = card['expansion'],
                is_maverick = card['is_maverick']
            )

            card_objs += [new_card]


        for deck in decks:
            deck_id = deck['id']
            del deck['is_my_deck']
            del deck['notes']
            del deck['is_my_favorite']
            del deck['is_on_my_watchlist']
            del deck['casual_wins']
            del deck['casual_losses']
            links = deck['_links']

            house_list = links['houses']
            deck_card_list = links['cards']
            
            bonus_amber, action, artifact, creature, upgrade, creature_pwr = get_deck_stats(deck_card_list, card_dict)

            new_deck = Deck2(
                name = deck['name'],
                expansion = deck['expansion'],
                power_level = deck['power_level'],
                chains = deck['chains'],
                wins = deck['wins'],
                losses = deck['losses'],
                id = deck['id'],
                bonus_amber = bonus_amber,
                num_action = action,
                num_artifact = artifact,
                num_creature = creature,
                num_upgrade = upgrade,
                creature_pwr = creature_pwr,
                house_list = house_list,
                card_list = deck_card_list
            )

            deck_objs += [new_deck]


        if page_count == 100:
            try:
                Deck2.objects.bulk_update(deck_objs, [
                    'name',
                    'expansion',
                    'power_level',
                    'chains',
                    'wins',
                    'losses',
                    'id',
                    'bonus_amber',
                    'num_action',
                    'num_artifact',
                    'num_creature',
                    'num_upgrade',
                    'creature_pwr',
                    'house_list',
                    'card_list'
                ])
            except:
                try:
                    Deck2.objects.bulk_create(deck_objs, batch_size=100, ignore_conflicts=True)
                    Card.objects.bulk_create(card_objs, batch_size=100, ignore_conflicts=True)

                    if Current_Page.objects.filter(id=1).exists():
                        Current_Page.objects.filter(id=1).update(page=page)
                        Current_Page.objects.filter(id=1).update(run_time=get_runtime())
                    else:
                        current_page = Current_Page.objects.create(id=1, page=page, run_time=get_runtime())
                        current_page.save()
                except:
                    logging.exception(f'{datetime.datetime.now()} Error when inserting data on page: {page}')
                    sleep(5)

            page_count = 0
            deck_objs = []
            card_objs = []


        print(page, '/', pages, ' ', end='')
        page += 1
        page_count += 1
        print(f'Page process time: {int(time.time() - start_time)} p_count: {page_count}')

        sleep(.5)

    get_runtime()
    
    
def assign_data(url):
    data = requests.get(url).json()     
    cards = data['_linked']['cards']
    decks = data['data']
    return (cards, decks)
    

def get_runtime():
    runtime = int(time.time() - program_start_time)

    if runtime/60/60 > 1:
        runtime = f'Previous run: {runtime//3600} hours and {int(runtime%3600/60)} minutes'
    elif runtime / 60 > 1:
        runtime = f'Previous run: {runtime//60} minutes and {int(runtime%60)} seconds'
    else:
        runtime = f'Previous run: {runtime} seconds'
    
    return runtime


def get_specific_deck(deck_id):
    url = f'https://www.keyforgegame.com/api/decks/{deck_id}/?links=cards'
    data = requests.get(url).json()   

    deck = data['data']
    deck_cards = data['data']['_links']['cards']
    cards = data['_linked']['cards']

    return (deck, deck_cards, cards)


def get_deck_stats(deck_list, card_list):
    amber = 0
    card_type = {
        'Action': 0,
        'Artifact': 0,
        'Creature': 0,
        'Upgrade': 0
    }
    creature_pwr = {}

    for card in deck_list:
        card_info = card_list[card]

        amber += card_info['amber']
        card_type[card_info['card_type']] += 1

        if card_info['power'] in creature_pwr:
            creature_pwr[card_info['power']] += 1
        elif card_info['power'] == 0:
            continue
        else:
            creature_pwr[card_info['power']] = 1

    return (amber, card_type['Action'], card_type['Artifact'], card_type['Creature'], card_type['Upgrade'], creature_pwr)


