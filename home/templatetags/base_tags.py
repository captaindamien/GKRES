from home.models import Footer, Contacts, HomePage, HomeService
from account.models import AccountServices
from django import template

from wagtail.models import Site

register = template.Library()

# ----- snippets -----

@register.inclusion_tag('../../gkres/templates/tags/footer.html', takes_context=True)
def footer_tag(context):
    return {
        'request': context['request'],
        'footer': Footer.objects.all(),
    }

 
@register.inclusion_tag('../../gkres/templates/tags/header.html', takes_context=True)
def header_tag(context):
    return {
        'request': context['request'],
    }


@register.inclusion_tag('../../gkres/templates/tags/user_header.html', takes_context=True)
def user_header_tag(context):
    return {
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/contacts.html', takes_context=True)
def contacts_tag(context):
    return {
        'request': context['request'],
        'contacts': Contacts.objects.all(),
    }

# ----- bakerydemo tags -----

@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context['request']).root_page


def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


def has_children(page):
    return page.get_children().live().exists()


def is_active(page, current_page):
    return (current_page.url_path.startswith(page.url_path) if current_page else False)


@register.inclusion_tag('tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    menuitems = parent.get_children().live().in_menu()
    for menuitem in menuitems:
        menuitem.show_dropdown = has_menu_children(menuitem)
        menuitem.active = (calling_page.url_path.startswith(menuitem.url_path)
                           if calling_page else False)

    # определение корневой страницы для корректного отображения в меню
    root_page = get_site_root(context)
    
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        'request': context['request'],
        'home_services': HomeService.objects.filter(service_id=root_page.id),    # передача пунктов таблицы HomeService в меню
        'account_services': AccountServices.objects.filter(service_id=root_page.id),
    }
    

@register.inclusion_tag('tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent, calling_page=None):
    menuitems_children = parent.get_children()
    menuitems_children = menuitems_children.live().in_menu()
    for menuitem in menuitems_children:
        menuitem.has_dropdown = has_menu_children(menuitem)
        menuitem.active = (calling_page.url_path.startswith(menuitem.url_path)
                           if calling_page else False)
        menuitem.children = menuitem.get_children().live().in_menu()
    return {
        'parent': parent,
        'menuitems_children': menuitems_children,
        'request': context['request'],
    }
