from random import choices
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import m2m_changed, post_save
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
    win_score = models.IntegerField(
        null = False,
        blank = False,
        default = 1,
        verbose_name = 'Количество очков за победу'
    )
    lose_score = models.IntegerField(
        null = False,
        blank = False,
        default = 0,
        verbose_name = 'Количество очков за поражение не в 0',
        help_text = 'Оставить 0 при стандартном ведении счета'
    )
    image = models.ImageField(
        upload_to = 'images/',
        blank = True,
        null = True,
        verbose_name = 'Изображение для окончания турнира'
    )
    is_end = models.BooleanField(
        default = False,
        verbose_name = 'Закончился турнир?'
    )
    f_place = models.CharField(
        max_length=200,
        null = True,
        blank = True,
        verbose_name='Первое место'
    )
    s_place = models.CharField(
        max_length=200,
        null = True,
        blank = True,
        verbose_name='Второе место'
    )
    th_place = models.CharField(
        max_length=200,
        null = True,
        blank = True,
        verbose_name='Третье место место'
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
    player_two = models.CharField(
        max_length = 100,
        blank = False,
        verbose_name = 'Второй игрок',
        default = '-'
    )
    player_one_score = models.IntegerField(
        default = 0,
        blank = False,
        null = False,
        verbose_name = f'Результат первого игрока'
    )
    player_two_score = models.IntegerField(
        default = 0,
        blank = False,
        null = False,
        verbose_name = 'Результат второго игрока'
    )
    set_statistic = models.CharField(
        max_length = 100,
        default = '0/0, 0/0',
        blank = False,
        null = False,
        verbose_name = 'Счет по геймам'
    )
    
    class Meta:
        verbose_name = f'Игра'
        verbose_name_plural = f'Игры'  
        
    def __str__(self):
        return f'Игра(ы) №{self.pk}'  


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