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


# TODO: Переделать функции заполнения таблиц в одну и оптимизировать запросы
def fill_table_pc(games, players, win_score, lose_score):
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
                for game in games.values():
                    # фильтруем на повторы и добавляем счет
                    if f'{player}:{players[i]}' == f'{game["player_one"]}:{game["player_two"]}':
                        table[f'{player}'].append(f'{game["player_one_score"]} - {game["player_two_score"]}')
                        
                        # итоговое кол-во очков за каждую победу
                        if game["player_one_score"] > game["player_two_score"] and game["player_two_score"] == 0:
                            player_score += win_score
                        elif game["player_one_score"] > game["player_two_score"] and game["player_two_score"] != 0:
                            player_score += win_score - lose_score
                        elif game["player_one_score"] < game["player_two_score"] and game["player_one_score"] != 0:
                            player_score += lose_score
                        
                    elif f'{player}:{players[i]}' == f'{game["player_two"]}:{game["player_one"]}':
                        # set_stat = ', '.join(game["set_statistic"][::-1].split(',')[::-1])[:-1]
                                        
                        table[f'{player}'].append(f'{game["player_two_score"]} - {game["player_one_score"]}')

                        if game["player_two_score"] > game["player_one_score"] and game["player_one_score"] == 0:
                            player_score += win_score
                        elif game["player_two_score"] > game["player_one_score"] and game["player_one_score"] != 0:
                            player_score += win_score - lose_score
                        elif game["player_two_score"] < game["player_one_score"] and game["player_two_score"] != 0:
                            player_score += lose_score
        
        table[f'{player}'].append(player_score)

    return table


def fill_table_mobile(games, players, win_score, lose_score):
    table = {}
    
    for player in players:
        table[f'{player}'] = []
        player_score = 0
        
        for i in range(len(players)):
            if player != players[i]:
                for game in games.values():
                    # фильтруем на повторы и добавляем счет
                    if f'{player}:{players[i]}' == f'{game["player_one"]}:{game["player_two"]}':
                        table[f'{player}'].append((players[i], f'{game["player_one_score"]} - {game["player_two_score"]}'))
                        
                        # итоговое кол-во очков за каждую победу
                        if game["player_one_score"] > game["player_two_score"] and game["player_two_score"] == 0:
                            player_score += win_score
                        elif game["player_one_score"] > game["player_two_score"] and game["player_two_score"] != 0:
                            player_score += win_score - lose_score
                        elif game["player_one_score"] < game["player_two_score"] and game["player_one_score"] != 0:
                            player_score += lose_score
                                
                    elif f'{player}:{players[i]}' == f'{game["player_two"]}:{game["player_one"]}':
                        table[f'{player}'].append((players[i], f'{game["player_two_score"]} - {game["player_one_score"]}'))
                        
                        if game["player_two_score"] > game["player_one_score"] and game["player_one_score"] == 0:
                            player_score += win_score
                        elif game["player_two_score"] > game["player_one_score"] and game["player_one_score"] != 0:
                            player_score += win_score - lose_score
                        elif game["player_two_score"] < game["player_one_score"] and game["player_two_score"] != 0:
                            player_score += lose_score
        
        table[f'{player}'].append(('Количество очков:', player_score))
    
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
    
    win_score = tour.win_score
    lose_score = tour.lose_score
    
    games = Games.objects.filter(tournament=tour)
    context['games'] = games
    
    players = tour.players.all()
    # context['players'] = players
    # context['players_count'] = range(len(players))
    
    # нужно для перерисовки таблиц под мобильные устройства
    if mobile(request):
        is_mobile = True
        table_mobile = fill_table_mobile(games, players, win_score, lose_score)
        context['table_mobile'] = table_mobile
    else:
        is_mobile = False   
        table_pc = fill_table_pc(games, players, win_score, lose_score)
        context['table_pc'] = table_pc
        
    context['is_mobile'] = is_mobile
    
    return render(request, 'tennis/tour.html', context=context)
