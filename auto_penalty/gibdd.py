import requests
import json

from .models import Car

test = Car.objects.get()

RES_SISTEMY_HEADERS = {
        'Authorization': f'Bearer eb42bbdd-8c22-403d-9e63-c9343403ef68'
        }


URL = "https://api.onlinegibdd.ru/v3/"
LIST_AUTO = "partner_auto/"
ADD_AUTO = "partner_auto/save/"


def add_auto(headers: dict, auto_cdi: str, auto_number: str, auto_region: str, auto_name: str) -> json:
    params = {
        'auto_cdi': auto_cdi,
        'auto_number': auto_number,
        'auto_region': auto_region,
        'auto_name': auto_name,
        }
    json_params = json.dumps(params)
    
    response = requests.post(
        f'{URL}{ADD_AUTO}',
        headers=headers,
        data=json_params,
        )
    
    return response.json()


def get_auto(headers: dict) -> json:
    response = requests.get(
        f'{URL}{LIST_AUTO}',
        headers=headers,
        )
    
    return response.json()

    
print(get_auto(RES_SISTEMY_HEADERS))