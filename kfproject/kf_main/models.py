from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import ArrayField

class Card(models.Model):
    id = models.TextField(primary_key=True)
    card_title = models.TextField(blank=True, null=True)
    house = models.TextField(blank=True, null=True)
    card_type = models.TextField(blank=True, null=True)
    front_image = models.TextField(blank=True, null=True)
    card_text = models.TextField(blank=True, null=True)
    traits = models.TextField(blank=True, null=True)
    amber = models.IntegerField(blank=True, null=True)
    power = models.IntegerField(blank=True, null=True)
    armor = models.IntegerField(blank=True, null=True)
    rarity = models.TextField(blank=True, null=True)
    flavor_text = models.TextField(blank=True, null=True)
    card_number = models.IntegerField(blank=True, null=True)
    expansion = models.IntegerField(blank=True, null=True)
    is_maverick = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'card'


class Current_Page(models.Model):
    page = models.IntegerField()
    id = models.IntegerField(primary_key=True)
    run_time = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'current_page'


class Deck(models.Model):
    name = models.TextField(blank=True, null=True)
    expansion = models.IntegerField(blank=True, null=True)
    power_level = models.IntegerField(blank=True, null=True)
    chains = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(blank=True, null=True)
    losses = models.IntegerField(blank=True, null=True)
    id = models.TextField(primary_key=True)
    num_action = models.IntegerField(blank=True, null=True)
    num_artifact = models.IntegerField(blank=True, null=True)
    num_creature = models.IntegerField(blank=True, null=True)
    num_upgrade = models.IntegerField(blank=True, null=True)
    bonus_amber = models.IntegerField(blank=True, null=True)
    creature_pwr = JSONField(blank=True, null=True)


    class Meta:
        managed = False 
        db_table = 'deck'


class Deck_Card(models.Model):
    deck = models.ForeignKey(Deck, models.DO_NOTHING, blank=True, null=True)
    card = models.ForeignKey(Card, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deck_card'


class Deck_House(models.Model):
    deck = models.ForeignKey(Deck, models.DO_NOTHING, blank=True, null=True)
    house = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deck_house'


class Deck2(models.Model):
    name = models.TextField(blank=True, null=True)
    expansion = models.IntegerField(blank=True, null=True)
    power_level = models.IntegerField(blank=True, null=True)
    chains = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(blank=True, null=True)
    losses = models.IntegerField(blank=True, null=True)
    id = models.TextField(primary_key=True)
    num_action = models.IntegerField(blank=True, null=True)
    num_artifact = models.IntegerField(blank=True, null=True)
    num_creature = models.IntegerField(blank=True, null=True)
    num_upgrade = models.IntegerField(blank=True, null=True)
    bonus_amber = models.IntegerField(blank=True, null=True)
    creature_pwr = JSONField(blank=True, null=True)
    house_list= ArrayField(models.TextField(), blank=True, null=True)
    card_list = ArrayField(models.TextField(), blank=True, null=True)


    class Meta:
        managed = True 
        db_table = 'deck2'
