from django.urls import path
from . import views

app_name = 'kf_main'

urlpatterns = [
    path('', views.index, name='index'),
    path('deck_search/', views.deck_search, name='deck_search'),
]