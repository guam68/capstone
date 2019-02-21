import requests
import re
import json
import time
from time import sleep
import datetime
import ast
# import credentials as cred
from psycopg2 import connect
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging


program_start_time = time.time()

logging.basicConfig(filename='error.log', filemode = 'a', level=logging.WARNING)
page = '1' 
site = ('https://www.keyforgegame.com/api/decks/?page=','&page_size=25&links=cards&ordering=date') 

# Get the number of pages required to process (working for v2)
def get_num_pages():
    response = requests.get(site[0] + page + site[1]).json()
    count = int(response['count'])
    pages = count // 25
    return pages

# Creates connection to database. Gets current page to be processed.
# Gets data with assign_data() and cleans before passing as parameters to functions
# Cycles through pages calling add_deck(), add_deck_houses(), add_deck_cards(), and get_cards()
def get_unique_cards(page, site):
    data = {} 
    cards = []
    decks = []
    con = connect(dbname='keyforge', user=cred.login['user'], host='localhost', password=cred.login['password'])

    get_page_sql = """
        select page from current_page;
    """

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute(get_page_sql)

    pages = get_num_pages()
    try:
        page = int(cur.fetchall()[0][0])
    except IndexError:
        page = 1
    finally:
        if page == pages:
            page = 1

    cur.close()
    
    for i in range(0, pages-page + 1): 
        url = site[0] + str(page) + site[1]
        start_time = time.time()
        card_list = []
        deck_list = []
        house_list = []
        deck_card_list = []

        try:
            data, cards, decks = assign_data(url)
           
        except:
            print('Error timeout. Sleeeeeep')
            sleep(5)
            print('Reattempting data retrieval')

            try:
                data, cards, decks = assign_data(url)
                print('Data collection successful.')
            except:
                logging.exception(f'{datetime.datetime.now()} Error retrieving data on page: {page}')

            continue

        for card in cards:
            card = list(card.values())
            card_list.append(card) 

        for deck in decks:
            deck_id = deck['id']
            del deck['is_my_deck']
            del deck['notes']
            del deck['is_my_favorite']
            del deck['is_on_my_watchlist']
            del deck['casual_wins']
            del deck['casual_losses']
            deck = list(deck.values())
            links = deck.pop(-1)

            house_list = links['houses']
            deck_card_list = links['cards']
            try:
                # Look into using a transaction here for queries (begin/commit)
                add_deck(deck, con)
                add_deck_houses(deck_id, house_list, con)
                add_deck_cards(deck_id, deck_card_list, con)
            except:
                logging.exception(f'{datetime.datetime.now()} Error when inserting data on page: {page}')
                sleep(5)

        try:
            add_cards(card_list, con, page)
        except:
            logging.exception(f'{datetime.datetime.now()} Error when inserting card data on page: {page}')
            sleep(5)

        print(page, '/', pages, ' ', end='')
        page += 1
        print('Page process time: ', int(time.time() - start_time))

        sleep(.5)
    
    
    con.close()


def assign_data(url):
    data = requests.get(url).json()     
    cards = data['_linked']['cards']
    decks = data['data']
    return (data, cards, decks)
    

# Last function called. Updates table with current page.
def add_cards(cards, con, page):
    for card in cards:
        sql = """
            insert into card
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on conflict do nothing;       
        """
        sql2 = """
        insert into current_page
        values(%s,%s,%s)
        on conflict (id) do update
        set (page, run_time) = (excluded.page, excluded.run_time)
        """

        runtime = get_runtime()
        cur = con.cursor()
        cur.execute(sql, (card))
        cur.execute(sql2, (page, 1, runtime))
        cur.close() 


def add_deck(deck, con):
    sql = """
        insert into deck
        values(%s,%s,%s,%s,%s,%s,%s)
        on conflict (id) do update
        set (power_level, chains, wins, losses)
        = (excluded.power_level, excluded.chains, excluded.wins, excluded.losses);
    """
    
    cur = con.cursor()
    cur.execute(sql, (deck))
    cur.close() 


def add_deck_houses(deck_id, house_list, con):
    cur = con.cursor()
    cur.execute('select count(*) as house_count from deck_house where deck_id=%s', (deck_id,))
    count = int(cur.fetchall()[0][0])

    for house in house_list:
        if count < 3:
            sql = """
                insert into deck_house
                values(%s,%s);       
            """
            cur.execute(sql, (deck_id, house))
            count+=1

    cur.close() 
    

def add_deck_cards(deck_id, deck_card_list, con):
    cur = con.cursor()
    cur.execute('select count(*) as card_count from deck_card where deck_id=%s', (deck_id,))
    count = int(cur.fetchall()[0][0])
    
    for card in deck_card_list:
        if count < 36:
            sql = """
                insert into deck_card
                values(%s, %s);       
            """
            add_list = [deck_id] + [card]
            cur.execute(sql, (add_list))
            count +=1
    
    cur.close()


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




