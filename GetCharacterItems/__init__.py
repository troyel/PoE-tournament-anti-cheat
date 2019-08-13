import datetime
import logging
import json

import azure.functions as func
import requests


def get_hero_items(rank,account,name):
    url_get_items = 'https://www.pathofexile.com/character-window/get-items'
    url_get_jewels = 'https://www.pathofexile.com/character-window/get-passive-skills?reqData=0?'

    hero_object = {}

    hero_object['rank'] = rank
    hero_object['character'] = {}
    hero_object['account'] = {}
    hero_object['character']['name'] = name
    hero_object['account']['name'] = account

    param = {'accountName': account, 'character': name}

    time.sleep(1)

    hero_object['equiped'] = requests.get(url=url_get_items, params=param).json()
    
    return hero_object


def main(hero: func.QueueMessage, blobout: func.Out[str]):
    logging.info('Python queue trigger function processed a queue item.')

    result = json.dumps({
        'id': hero.id,
        'body': hero.get_body().decode('utf-8'),
        'expiration_time': (hero.expiration_time.isoformat()
                            if hero.expiration_time else None),
        'insertion_time': (hero.insertion_time.isoformat()
                           if hero.insertion_time else None),
        'time_next_visible': (hero.time_next_visible.isoformat()
                              if hero.time_next_visible else None),
        'pop_receipt': hero.pop_receipt,
        'dequeue_count': hero.dequeue_count
    })
    print(result)
    quelist =  str(hero.get_body().decode('utf-8')).split(';')
    
    print(quelist)

    hero_object = get_hero_items(quelist[0], quelist[1], quelist[2])

    if hero_object:
        blobout.set(json.dumps(hero_object))
    else:
        print('Hero Object Empty - likely HTTP API FAIL')

    logging.info(result)