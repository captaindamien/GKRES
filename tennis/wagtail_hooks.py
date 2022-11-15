from wagtail.contrib.modeladmin.options import (
    ModelAdmin, 
    ModelAdminGroup, 
    modeladmin_register 
)

from .models import Tournaments, Games, Players
    

class TournamentsAdmin(ModelAdmin):
    model = Tournaments 
    menu_label = "Турниры"  
    menu_icon = "site" 
    menu_order = 200 
    add_to_settings_menu = False 
    exclude_from_explorer = False 
    list_display = ("name", "date")
    list_filter = ("name", "date", "players")
    search_fields = ("name", "date")
    

class GamesAdmin(ModelAdmin):
    model = Games 
    menu_label = "Игры"  
    menu_icon = "table" 
    menu_order = 200 
    add_to_settings_menu = False 
    exclude_from_explorer = False 
    list_display = ("tournament", "date", "player_one", "player_two")
    list_filter = ("tournament", "date", "player_one", "player_two")
    search_fields = ("tournament", "date", "player_one", "player_two")


class PlayersAdmin(ModelAdmin):
    model = Players 
    menu_label = "Игроки"  
    menu_icon = "group" 
    menu_order = 200 
    add_to_settings_menu = False 
    exclude_from_explorer = False 


class TennisGroup(ModelAdminGroup):
    menu_label = "Теннис" 
    menu_icon = "pick"
    menu_order = 500 
    items = (TournamentsAdmin, GamesAdmin, PlayersAdmin)


modeladmin_register(TennisGroup)