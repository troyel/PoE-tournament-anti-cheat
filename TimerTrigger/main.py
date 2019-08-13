#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Getters for characters, items and passive tree jewels for a league.
Uses ladder, character and passive api from GGG
"""

import datetime
import logging
import importlib
import typing

import azure.functions as func
import sys
import gzip
import requests
import time
import json

importlib.reload(sys.modules['azure'])

def all_chars_from_ladder(url, dump=False):
    def get_total_and_time():
        params = {'offset': 0, 'limit': 1}
        # TODO: Be nice and do some fallback stuff
        r = requests.get(url=url, params=params)
        data_ = r.json()
        if 'cached_since' in data_:
            return data_['total'], data_['cached_since']
        else:
            return data_['total'], None

    def get_chars(offset_, limit_):
        params = {'offset': offset_, 'limit': limit_}
        time.sleep(1.5)
        # TODO: Be nice and do some fallback stuff
        r = requests.get(url=url, params=params)
        data_ = r.json()
        return data_['entries']

    total, time_cached = get_total_and_time()
    total_left = total
    all_chars_ = []
    print("Total:", total, "cached at:", time_cached)
    while total_left > 0:
        offset = total - total_left
        if total_left > 200:
            limit = 200
        else:
            limit = total_left
        all_chars_.extend(get_chars(offset, limit))
        total_left = total_left - limit
        print("# left:", total_left)
    print("Done")
    if dump:
        fname = "/ladder_" + time.strftime("%Y%m%d-%H%M%S") + '.json.gz'
        print("Dumping to file: " + fname)
        with gzip.GzipFile(fname, 'w') as fout:
            fout.write(json.dumps(all_chars_).encode('utf-8'))
    return all_chars_






def main(mytimer: func.TimerRequest, blobout: func.Out[str], msg: func.Out[typing.List[str]]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    URL = "http://api.pathofexile.com/ladders/Slippery Hobo League (PL5357)"
    responce = all_chars_from_ladder(URL, dump = False)
    
    length = len(responce)
    
    newlist = []

    for item in responce:
        newlist.append(str(item['rank'])+";"+str(item['account']['name'])+";"+str(item['character']['name']))
    
    msg.set(newlist)

    blobout.set(json.dumps(responce))
    print("Saved json response of all characters to BLOB")
    

    logging.info('Python timer trigger function ran at %s', utc_timestamp)