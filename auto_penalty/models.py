from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete

import requests
import json


class Org(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Наименование организации',
        blank=False,
        null=False,
        default='',
    )
    inn = models.CharField(
        max_length=10,
        verbose_name='ИНН организации',
        blank=False,
        null=False,
        default='',
    )
    api = models.CharField(
        max_length=100,
        verbose_name='API-ключ ГИБДД организации',
        blank=False,
        null=False,
        default='',
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = f'Организация'
        verbose_name_plural = f'Организации'  


class Car(models.Model):
    organization = models.ForeignKey(
        'Org',
        on_delete = models.CASCADE,
        unique=False,
        verbose_name = 'Владелец авто',
    )
    gibdd_id = models.IntegerField(
        default=0,
        editable=False,
        verbose_name='ID присвоенный ГИБДД',
        help_text='Если указан 0 - значит атво в ГИБДД не значится',
    )
    cdi = models.CharField(
        max_length=10,
        verbose_name='СТС',
        blank=False,
        null=False,
    )
    number = models.CharField(
        max_length=6,
        verbose_name='Госномер авто (без региона)',
        blank=False,
        null=False,
    )
    region = models.CharField(
        max_length=3,
        verbose_name='Регион авто',
        blank=False,
        null=False,
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Название авто',
        blank=False,
        null=False,
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = f'Авто'
        verbose_name_plural = f'Авто'  



URL = "https://api.onlinegibdd.ru/v3/"


def connect_api(instance) -> dict or False:
    LIST_AUTO = "partner_auto/"

    org = Org.objects.get(name=instance.organization)
    api_key = org.api

    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    #проверка ответа от ГИБДД
    test_auth = requests.get(
        f'{URL}{LIST_AUTO}',
        headers=headers,
        )
    
    if test_auth.status_code == 200:
        return headers
    else:
        return False

@receiver(pre_save, sender=Car)
def add_gibdd(sender, instance, **kwargs):
    ADD_AUTO = "partner_auto/save/"
    
    headers = connect_api(instance=instance)
    
    if headers != False:        
        params = {
            'auto_cdi': instance.cdi,
            'auto_number': instance.number,
            'auto_region': instance.region,
            'auto_name': instance.name,
            }
        json_params = json.dumps(params)
        
        # отправка в ГИБДД
        add_auto = requests.post(
            f'{URL}{ADD_AUTO}',
            headers=headers,
            data=json_params,
            )
        if add_auto.status_code == 200:
            # меняем id в модели на присвоенный от ГИБДД
            instance.gibdd_id = add_auto.json()['data']['id']
        else:
            raise Exception(f'{add_auto.json()["errors"]}')
    else:
        raise Exception(f'Ошибка соединения с ГИБДД')


@receiver(pre_delete, sender=Car)
def delete_gibdd(sender, instance, **kwargs):
    DELETE_AUTO = "partner_auto/delete/"
    
    headers = connect_api(instance=instance)
    
    if headers != False:
        params = {
            'id': instance.gibdd_id,
        }
        json_params = json.dumps(params)
        
        # Удаление в ГИБДД
        delete_auto = requests.post(
            f'{URL}{DELETE_AUTO}',
            headers=headers,
            data=json_params,
            )
        if delete_auto.status_code != 200:
            raise Exception(f'{delete_auto.json()["errors"]}')
    else:
        raise Exception(f'Ошибка соединения с ГИБДД')        


class Penalty(models.Model):
    # status = models.CharField(
    #     max_length=50,
    #     verbose_name='Статус оплаты',
    #     blank=False,
    #     null=False,
    # )
    # auto_id = models.IntegerField
    pass
