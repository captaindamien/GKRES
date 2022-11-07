from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Tournaments, Games, Players
from datetime import datetime
from django.db.models import Q
import re


def mobile(request):
    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False


def fill_table_pc(games, players):
    # итоговая таблица с данными
    table = {}
    for player in players:
        # пустой список для каждого игрока для будущего наполнения
        table[f'{player}'] = []
        # счетчик очков
        player_score = 0
        
        for i in range(len(players)):
            # если игроки совпадают
            if player == players[i]:
                table[f'{player}'].append(f'-')
            # если нет
            else: 
                for game in games:
                    # фильтруем на повторы и добавляем счет
                    if f'{player}:{players[i]}' == f'{game.player_one}:{game.player_two}':
                        table[f'{player}'].append(f'{game.player_one_score} - {game.player_two_score}')
                        # итоговое кол-во очков за каждую победу
                        if game.player_one_score > game.player_two_score:
                            player_score += 1
                    elif f'{player}:{players[i]}' == f'{game.player_two}:{game.player_one}':
                        table[f'{player}'].append(f'{game.player_two_score} - {game.player_one_score}')
                        if game.player_two_score > game.player_one_score:
                            player_score += 1
        
        table[f'{player}'].append(player_score)

    return table


def fill_table_mobile(games, players):
    table = {}
    
    for player in players:
        table[f'{player}'] = []
        player_score = 0
        
        for i in range(len(players)):
            if player != players[i]:
                for game in games:
                    # фильтруем на повторы и добавляем счет
                    if f'{player}:{players[i]}' == f'{game.player_one}:{game.player_two}':
                        table[f'{player}'].append((players[i] ,f'{game.player_one_score} - {game.player_two_score}'))
                        # итоговое кол-во очков за каждую победу
                        if game.player_one_score > game.player_two_score:
                            player_score += 1
                    elif f'{player}:{players[i]}' == f'{game.player_two}:{game.player_one}':
                        table[f'{player}'].append((players[i] ,f'{game.player_two_score} - {game.player_one_score}'))
                        if game.player_two_score > game.player_one_score:
                            player_score += 1
        
        table[f'{player}'].append(('Количество очков:' ,player_score))
    
    return table


def tennis_tournaments(request):
    context = {}
    tours = Tournaments.objects.all()
    context['tours'] = tours
    context['now'] = datetime.now()
    context['user'] = request.user
    
    return render(request, 'tennis/tournaments.html', context=context)


def tournament(request, pk):
    context = {}
    
    tour = Tournaments.objects.get(pk=pk)
    context['tour'] = tour
    
    games = Games.objects.filter(tournament=tour)
    context['games'] = games
    
    players = tour.players.all()
    context['players'] = players
    context['players_count'] = range(len(players))
    
    # # итоговая таблица с данными
    # table = {}
    # for player in players:
    #     # пустой список для каждого игрока для будущего наполнения
    #     table[f'{player}'] = []
    #     # счетчик очков
    #     player_score = 0
        
    #     for i in range(len(players)):
    #         # если игроки совпадают
    #         if player == players[i]:
    #             table[f'{player}'].append(f'-')
    #         # если нет
    #         else: 
    #             for game in games:
    #                 # фильтруем на повторы и добавляем счет
    #                 if f'{player}:{players[i]}' == f'{game.player_one}:{game.player_two}':
    #                     table[f'{player}'].append(f'{game.player_one_score} - {game.player_two_score}')
    #                     # итоговое кол-во очков за каждую победу
    #                     if game.player_one_score > game.player_two_score:
    #                         player_score += 1
    #                 elif f'{player}:{players[i]}' == f'{game.player_two}:{game.player_one}':
    #                     table[f'{player}'].append(f'{game.player_two_score} - {game.player_one_score}')
    #                     if game.player_two_score > game.player_one_score:
    #                         player_score += 1
        
    #     table[f'{player}'].append(player_score)
    table_pc = fill_table_pc(games, players)
    context['table_pc'] = table_pc
    
    # нужно для перерисовки таблиц под мобильные устройства
    if mobile(request):
        is_mobile = True
    else:
        is_mobile = False
    context['is_mobile'] = is_mobile
    
    table_mobile = fill_table_mobile(games, players)
    context['table_mobile'] = table_mobile
    
    print(table_mobile)
    
    return render(request, 'tennis/tour.html', context=context)
