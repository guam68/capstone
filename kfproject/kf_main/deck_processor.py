from .models import Deck, Card, Deck_Card, Deck_House


def set_deck_attrib():
    deck_list = Deck.objects.filter(num_action__isnull=True)
    print(len(deck_list))
    count= 0
    total_processed = {
        'processed': 0,
        'saved': 0
    }
    deck_objs = []


    for deck in deck_list:
        deck_cards = Card.objects.filter(deck_card__deck_id=deck.id)
        amber = 0
        card_type = {
            'Action': 0,
            'Artifact': 0,
            'Creature': 0,
            'Upgrade': 0
        }
        creature_pwr = {}

        for card in deck_cards:
            amber += card.amber
            card_type[card.card_type] += 1

            if card.power in creature_pwr:
                creature_pwr[card.power] += 1
            elif card.power == 0:
                continue
            else:
                creature_pwr[card.power] = 1

        deck.bonus_amber = amber
        deck.num_action = card_type['Action']
        deck.num_artifact = card_type['Artifact']
        deck.num_creature = card_type['Creature']
        deck.num_upgrade = card_type['Upgrade']
        deck.creature_pwr = creature_pwr
        deck_objs += [deck]
        count += 1
        total_processed['processed'] += 1

        if count == 100  or count == len(deck_list):
            Deck.objects.bulk_update(deck_objs, ['bonus_amber', 'num_action', 'num_artifact', 'num_creature', 'num_upgrade', 'creature_pwr'])
            count = 0
            total_processed['saved'] += len(deck_objs) 
            deck_objs = []

        print(f'Processed: {total_processed["processed"]}\tSaved: {total_processed["saved"]}')

