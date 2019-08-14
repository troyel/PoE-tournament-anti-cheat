import azure.functions as func
import datetime
import time
import logging
import json
import requests
from lxml.html import fromstring
import random


def get_proxies():
    url = 'https://sslproxies.org/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = []
    for i in parser.xpath('//tbody/tr')[:100]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy)
    return proxies

def get_response(url_call, parameters):
    proxies = get_proxies()
    if len(proxies) < 1:
        print("PROXIES ARE NOT AVAILABLE!")
        raise Exception(proxies)
    for i in range(1,11):
        #Get a proxy from the pool
        proxy = proxies[random.randint(0,len(proxies))]
        
        #print(url_call)
        #print(parameters)

        #print("proxy :"+str(proxy))
        print("Request #%d"%i)
        try:
            response = requests.get(url = url_call, params=parameters ,proxies={"http": proxy, "https": proxy})
            print(str(response)[:15])
            return response.json()
        except:
            #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
            #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
            print("Skipping. Connnection error")

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

    time.sleep(1.25)

    hero_object['equiped'] = get_response(url_get_items, param)
    
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
    #print(result)
    quelist =  str(hero.get_body().decode('utf-8')).split(';')
    
    #print(quelist)

    hero_object = get_hero_items(quelist[0], quelist[1], quelist[2])

    try:
        if hero_object['equiped']['error'] :
            logging.info("/n error raised /n"+json.dumps(hero_object))
            raise Exception(json.dumps(hero_object['equiped']['error']))
        else:
            blobout.set(json.dumps(hero_object))
    except:
        blobout.set(json.dumps(hero_object))
        
    logging.info(result)