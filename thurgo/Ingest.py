import sqlite3
import urllib.request
import json
from operator import itemgetter
import math
import datetime
import time


def current_timestamp():
    return int(datetime.datetime.now(
        datetime.timezone.utc).timestamp())

def current_time_interval_start():
    current_time = current_timestamp()
    fifth_minute = 5 * 60
    return int((current_time // fifth_minute) * fifth_minute)

def retrieve_exchange_data():
    #TODO: Rewrite with a better api
    ge = None
    retry = 20
    backoff = 5
    tries = 0
    while not ge and tries < retry:
        try:
            RSBUDDY = 'https://rsbuddy.com/exchange/summary.json'
            req = urllib.request.Request(RSBUDDY)
            res = urllib.request.urlopen(req).read()
            ge = json.loads(res.decode('utf-8'))
        except Exception as e:
            tries += 1
            print(e)
            print(f'RSBuddy request failed. Retrying in a {backoff} seconds.')
            time.sleep(backoff)
    return ge

def create_ge_table(c, ge):
    c.execute('''CREATE TABLE ge
                 (datetime integer,
                  item_id integer,
                  bid integer,
                  ask integer,
                  avg_price integer,
                  buy_volume integer,
                  sell_volume integer,
                  total_volume integer)''')



def create_items_table(c, ge):
    c.execute('DROP TABLE items')
    c.execute('''CREATE TABLE items
                 (item_id integer,
                  member integer,
                  shop_price integer,
                  high_alch integer,
                  low_alch integer,
                  buy_limit,
                  name text
                  )''')

    item_info = 'https://raw.githubusercontent.com/Coffee-fueled-deadlines/OSRS-JSON-Item-Information/master/item_information.json'
    req = urllib.request.Request(item_info)
    res = urllib.request.urlopen(req).read()
    item_info = json.loads(res.decode('utf-8'))

    rows = []
    for item in ge.values():
        name = item['name']
        if name.lower() in item_info:
            extra = (
                item_info[name.lower()]['high_alch_price'],
                item_info[name.lower()]['low_alch_price'],
                item_info[name.lower()]['buy_limit'])
        else:
            extra = (-1, -1, -1)

        rows.append((
            item['id'],
            item['members'],
            item['sp'],
            *extra,
            name,
            ))
    c.executemany('''INSERT INTO items (
                        item_id,
                        member,
                        shop_price,
                        high_alch,
                        low_alch,
                        buy_limit,
                        name)
                     values (?, ?, ?, ?, ?, ?, ?)
                  ''', rows)

def insert_data(c, rows):
    c.executemany('''INSERT INTO ge (
                        datetime,
                        item_id,
                        bid,
                        ask,
                        avg_price,
                        buy_volume,
                        sell_volume,
                        total_volume)
                     values (?, ?, ?, ?, ?, ?, ?, ?)
                  ''', rows)

def get_last_db_time(c):
    c.execute('SELECT datetime FROM ge ORDER BY datetime DESC LIMIT 1')
    return c.fetchone()[0]

def bulk_ingest_ge(c):
    ge = retrieve_exchange_data()
    rows = []
    for item in ge.values():
        rows.append((
            interval_time,
            item['id'],
            item['buy_average'],
            item['sell_average'],
            item['overall_average'],
            item['buy_quantity'],
            item['sell_quantity'],
            item['overall_quantity']))
    
    insert_data(c, rows)

conn = sqlite3.connect('ge.db')
c = conn.cursor()

while True:
    interval_time = current_time_interval_start()
    print(f'Current interval time: {interval_time}')

    if interval_time > get_last_db_time(c):
        print('Inserting updated Grand Exchange quotes!')

        bulk_ingest_ge(c)
        conn.commit()
    else:
        print('No new Grand Exchange data yet.')

    wait_time = current_time_interval_start() + (5 * 60) - current_timestamp() + 1
    print(f'Sleeping for {wait_time} seconds until the next time interval..\n')
    time.sleep(wait_time)
