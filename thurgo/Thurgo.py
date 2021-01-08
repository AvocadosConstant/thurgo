import urllib.request
import json
from operator import itemgetter
import math
import sqlite3


RSBUDDY = 'https://rsbuddy.com/exchange/summary.json'
req = urllib.request.Request(RSBUDDY)
res = urllib.request.urlopen(req).read()
ge =  json.loads(res.decode('utf-8'))
#print(ge['1953'])

portfolio = [
    'oak logs',
    'mithril arrow',
    'gold ore',
    'mithril platebody',
    'banana',
    'salmon',
    'yellow dye',
    'adamant chainbody']


for item in ge.values():
    item['spread'] = item['sell_average'] - item['buy_average']
    item['bsr'] = math.inf if not item['sell_quantity'] else item['buy_quantity']/(item['sell_quantity'])
    item['margin'] = 0 if not item['buy_average'] else item['spread']/item['buy_average']

print(f"   item                spread\tprice\tbid\task\tvolume\t\tbuy vol\t\tsell vol\tbsr\tmargin")
for key, item in sorted(
        ge.items(), key=lambda item: item[1]['overall_quantity'], reverse=True):
    break
    if (item['name'].lower() in portfolio or
        (not item['members']
        #and 'logs' in item['name'].lower()
        and item['overall_quantity'] > 700
        and abs(item['spread']) >= 1
        and item['bsr'] > .1 and item['bsr'] < 20 
        and abs(item['margin']) > .02
        )):

        pick = " * " if item['name'].lower() in portfolio else "   "
        print(f"{pick}{item['name']:20}"
              f"\t{item['spread']}"
              f"\t{item['buy_average']:,}"
              f"\t{item['sell_average']:,}"
              f"\t{item['overall_quantity']:,}"
              f"\t\t{item['buy_quantity']:,}"
              f"\t\t{item['sell_quantity']:,}"
              f"\t\t{item['bsr']:.3f}"
              f"\t{100*item['margin']:.3f}%")

pd_in = [
    "jug of water",
    "pot of flour"]
pd_out = [
    "pastry dough",
    "jug",
    "pot",
    "chocolate bar",
    "chocolate dust",
    ]

brian = [
    "steel arrow",
    "oak shortbow",
    "willow shortbow",
    "maple shortbow",
    "oak longbow",
    "willow longbow",
    "maple longbow",
    ]
for key, item in ge.items():
    #if item['name'].lower() in pd_in or item['name'].lower() in pd_out:
    if item['name'].lower() in brian:

        print(f"   {item['name']:20}"
              f"\t{item['spread']}"
              f"\t{item['overall_average']:,}"
              f"\t{item['buy_average']:,}"
              f"\t{item['sell_average']:,}"
              f"\t{item['overall_quantity']:,}"
              f"\t\t{item['buy_quantity']:,}"
              f"\t\t{item['sell_quantity']:,}"
              f"\t\t{item['bsr']:.3f}"
              f"\t{100*item['margin']:.3f}%")


"""
conn = sqlite3.connect('ge.db')
c = conn.cursor()
c.execute('''SELECT datetime(datetime, 'unixepoch', 'localtime') as datetime,
                    ask - bid as spread,
                    bid,
                    ask,
                    avg_price,
                    buy_volume,
                    sell_volume,
                    total_volume
             FROM ge
             WHERE item_id=1521
             ORDER BY datetime DESC;
             ''')
for row in c.execute('''SELECT datetime(datetime, 'unixepoch', 'localtime') as datetime,
                               avg_price,
                               total_volume
                        FROM ge
                        INNER JOIN items
                            ON items.item_id = ge.item_id
                        WHERE name LIKE '%Oak logs%'
                        ORDER BY datetime DESC;
                        '''):
    #print(row, end=' ')
    #print(row[0], row[1], '*' * row[1])
    pass
"""
