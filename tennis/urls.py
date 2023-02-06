from django.urls import path
from .views import tennis_tournaments, tournament

app_name = 'tennis'

urlpatterns = [
    path('tennis-tournaments/', tennis_tournaments, name="tennis-tournaments"),
    path('tournament/<int:pk>', tournament, name='tournament')
]
