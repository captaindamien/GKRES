from random import choices
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import m2m_changed
from django.dispatch import receiver


class Tournaments(models.Model):
    name = models.CharField(
        max_length = 100,
        blank = False,
        unique=True,
        verbose_name = 'Название турнира',
    )
    date = models.DateTimeField(
        default = timezone.now,
        verbose_name = 'Дата и время начала турнира'
    )
    players = models.ManyToManyField(
        'Players',
        verbose_name = "Участники",
    )
    tour_format = models.CharField(
        max_length = 50,
        blank = False,
        choices = [
            ('круговая', 'круговая'),
            ('плей-офф', 'плей-офф')    
        ],
        verbose_name = 'Формат проведения',
        default = 'круговая',
    )
    is_end = models.BooleanField(
        default = False,
        verbose_name = 'Закончился турнир?'
    )
    
    def __str__(self):
        return self.name  


class Games(models.Model):
    tournament = models.ForeignKey(
        'Tournaments',
        on_delete = models.CASCADE,
        unique=False,
        verbose_name = 'Игра турнира',
    )
    date = models.DateTimeField(
        blank = True,
        null = True,
        verbose_name = 'Дата и время проведения игры'
    )
    player_one = models.CharField(
        max_length = 100,
        blank = False,
        verbose_name = 'Первый игрок',
        default = '-'
    )
    player_one_score = models.IntegerField(
        default = 0
    )
    player_one_set_1 = models.IntegerField(
	default = 0
    )
    player_one_set_2 = models.IntegerField(
        default = 0
    )
    player_one_tie = models.IntegerField(
        default = 0
    )
    player_two = models.CharField(
        max_length = 100,
        blank = False,
        verbose_name = 'Второй игрок',
        default = '-'
    )
    player_two_score = models.IntegerField(
        default = 0
    )
    player_two_set_1 = models.IntegerField(
        default = 0
    )
    player_two_set_2 = models.IntegerField(
        default = 0
    )
    player_two_tie = models.IntegerField(
        default = 0
    )


class Players(models.Model):
    player = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        verbose_name = 'Участники',
    )
    
    def __str__(self):
        return f'{self.player.first_name} {self.player.last_name}'


def create_games(sender, instance, **kwargs):
    tour_players_query = instance.players.all()
    tour_players = [f'{player}' for player in tour_players_query]

    games = [[tour_players[i], tour_player] for tour_player in tour_players for i in range(len(tour_players) - 1)]
    [games.remove(j) for j in games if j[0] == j[1]]

    for k in games:
        for l in games:
            if l[0] + l[1] == k[1] + k[0]:
                games.remove(l)

    for game in games:
        Games.objects.create(
            tournament = instance,
            player_one = game[0],
            player_two = game[1],
        )


m2m_changed.connect(create_games, sender=Tournaments.players.through)  