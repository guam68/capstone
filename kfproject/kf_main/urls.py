from django.urls import path
from . import views

app_name = 'kf_main'

urlpatterns = [
    path('', views.index, name='index'),
    path('deck_search/', views.deck_search, name='deck_search'),
    path('deck_detail/<str:deck_id>', views.deck_detail, name='deck_detail'),
    path('nodes/', views.get_nodes, name='get_nodes'),
    path('tooltip/', views.get_tooltip, name='get_tooltip'),
    path('top100/', views.get_top100, name='get_top100'),
    path('search/', views.search, name='search'),
    path('get_card_freq/', views.get_card_freq, name='get_card_freq')
]