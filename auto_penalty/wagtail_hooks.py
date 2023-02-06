from wagtail.contrib.modeladmin.options import (
    ModelAdmin, 
    ModelAdminGroup, 
    modeladmin_register 
)

from .models import Org, Car, Penalty
    

class OrgAdmin(ModelAdmin):
    model = Org 
    menu_label = "Организации"  
    menu_icon = "group" 
    menu_order = 200 
    add_to_settings_menu = False 
    exclude_from_explorer = False 
    list_display = ("name", "inn", "api",)
    list_filter = ("name",)
    search_fields = ("name",)
    

class CarAdmin(ModelAdmin):
    model = Car
    menu_label = "Автомобили"  
    menu_icon = "spinner" 
    menu_order = 200 
    add_to_settings_menu = False 
    exclude_from_explorer = False 
    list_display = ("name", "organization", "gibdd_id", "cdi", "number")
    list_filter = ("organization", "region")
    search_fields = ("name", "organization", "gibdd_id", "cdi", "number")
    readonly_fields = ('gibdd_id')


class PenaltyAdmin(ModelAdmin):
    model = Penalty 
    menu_label = "Штрафы"  
    menu_icon = "lock" 
    menu_order = 200 
    add_to_settings_menu = False 
    exclude_from_explorer = False 


class PenaltyGroup(ModelAdminGroup):
    menu_label = "Штрафы ГИБДД" 
    menu_icon = "warning"
    menu_order = 500 
    items = (OrgAdmin, CarAdmin, PenaltyAdmin)


modeladmin_register(PenaltyGroup)